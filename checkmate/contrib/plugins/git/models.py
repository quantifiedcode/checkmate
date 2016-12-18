# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid
import time
import datetime
import logging
import copy
import traceback

logger = logging.getLogger(__name__)

from blitzdb.fields import (DateTimeField,
                            CharField,
                            IntegerField,
                            ForeignKeyField,
                            EnumField,
                            TextField,
                            ManyToManyField)

from checkmate.lib.models import (Snapshot,
                                  Project,
                                  BaseDocument,
                                  FileRevision,
                                  Diff,
                                  IssueOccurrence)
from .lib.repository import Repository
from checkmate.helpers.hashing import Hasher

class GitRepository(BaseDocument):

    path_ = CharField(indexed=True)
    project = ForeignKeyField('Project', backref = 'git', unique=True)
    default_branch = CharField(indexed=True)

    @property
    def path(self):
        return self.path_

    @path.setter
    def path(self, path):
        self.path_ = path

    def get_settings(self):
        default_branch = self.get_default_branch()
        if default_branch is None:
            return
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
        return

    @property
    def repository(self):
        if not hasattr(self,'_repository'):
            self._repository = Repository(self.path)
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
            file_revision._file_content = lambda commit_sha = commit_sha, file_revision = file_revision: self.repository.get_file_content(commit_sha,file_revision.path)
            file_revisions.append(file_revision)
        return file_revisions

    def get_default_branch(self):
        branches = self.repository.get_branches()
        if self.default_branch in branches:
            return self.default_branch
        elif 'origin/master' in branches:
            return 'origin/master'
        elif branches:
            return branches[0]
        else:
            return

class GitSnapshot(BaseDocument):

    """
    """

    project = ForeignKeyField('Project',unique = False,backref = 'git_snapshots')
    snapshot = ForeignKeyField('Snapshot',unique = True,backref = 'git_snapshot')
    sha = CharField(indexed = True,length = 40)
    hash = CharField(indexed = True,length = 64)
    committer_date = DateTimeField(indexed = True)
    author_date = DateTimeField(indexed = True)
    author_name = CharField(length = 100)
    committer_date_ts = IntegerField(indexed = True)
    author_date_ts = IntegerField(indexed = True)
    tree_sha = CharField(indexed = True,length = 40)
    log = TextField(indexed = False)

    class Meta(BaseDocument.Meta):

        unique_together = [('project','sha')]

class GitBranch(BaseDocument):

    project = ForeignKeyField('Project',backref = 'git_branches')
    name = CharField(indexed = True,length = 100)
    hash = CharField(indexed = True,length = 64)
    remote = CharField(indexed = True,length = 100)
    last_analyzed_snapshot = ForeignKeyField('GitSnapshot')
    head_snapshot = ForeignKeyField('GitSnapshot')

    class Meta(BaseDocument.Meta):

        unique_together = [('project','name')]
