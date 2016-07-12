from .lib.repository import Repository
from .models import GitSnapshot
from checkmate.lib.models import FileRevision
from checkmate.helpers.hashing import Hasher

import traceback
import datetime
import uuid
import logging
import yaml

logger = logging.getLogger()

class Git(object):

    def __init__(self,project):
        self.project = project

    class SettingsValidationError(BaseException):

        def __init__(self,errors):
            self.errors = errors

    def get_settings(self):
        default_branch = self.get_default_branch()
        branches = self.repository.get_branches()
        if default_branch in branches:
            latest_commit = self.repository.get_commits(default_branch,limit = 1)[0]
            try:
                checkmate_file_content = self.repository\
                                 .get_file_content(latest_commit['sha'],'.checkmate.yml')
                try:
                    checkmate_settings = yaml.load(checkmate_file_content)
                    return checkmate_settings
                except:
                    raise ValueError("Cannot parse checkmate YML file!")
            except:
                logger.warning("No .checkmate.yml file found!")
        return None

    @property
    def repository(self):
        if not hasattr(self,'_repository'):
            self._repository = Repository(self.project.path)
        return self._repository

    def get_snapshots(self,**kwargs):
        """
        Returns a list of snapshots in a given repository.
        """
        commits = self.repository.get_commits(**kwargs)
        snapshots = []
        for commit in commits:
            for key in ('committer_date','author_date'):
                commit[key] = datetime.datetime.fromtimestamp(commit[key+'_ts'])
            snapshot = GitSnapshot(commit)
            hasher = Hasher()
            hasher.add(snapshot.sha)
            snapshot.hash = hasher.digest.hexdigest()
            snapshot.project = self.project
            snapshot.pk = uuid.uuid4().hex
            snapshots.append(snapshot)
        return snapshots

    def get_file_revisions(self,commit_sha, filters = None):

        files = self.repository.get_files_in_commit(commit_sha)

        if filters:
            for filter_func in filters:
                files = [f for f in files if f['path'] in filter_func([ff['path'] for ff in files])]

        file_revisions = []
        for file_obj in files:

            hasher = Hasher()
            file_revision = FileRevision(file_obj)

            hasher.add(file_revision.path)
            hasher.add(file_revision.sha)

            file_revision.project = self.project
            file_revision.hash = hasher.digest.hexdigest()
            file_revision.pk = uuid.uuid4().hex
            file_revision._file_content = lambda commit_sha = commit_sha,file_revision = file_revision: self.repository.get_file_content(commit_sha,file_revision.path)
            file_revisions.append(file_revision)
        return file_revisions

    def get_default_branch(self):
        branches = self.repository.get_branches()
        if 'default_branch' in self.project and self.project.default_branch in branches:
            return self.project.default_branch
        elif 'github_data' in self.project and 'default_branch' in self.project.github_data \
          and 'origin/'+self.project.github_data['default_branch'] in branches:
            return 'origin/'+self.project.github_data['default_branch']
        elif 'master' in branches:
            return 'master'
        elif 'origin/master' in branches:
            return 'origin/master'
        elif branches:
            return branches[0]
        else:
            raise AttributeError("No default branch defined!")
