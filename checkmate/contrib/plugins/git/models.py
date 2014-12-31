# -*- coding: utf-8 -*-
"""
This file is part of checkmate, a meta code checker written in Python.

Copyright (C) 2015 Andreas Dewes, QuantifiedCode UG

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import os
import uuid
import time
import datetime
import logging

logger = logging.getLogger(__name__)

from .lib.repository import Repository
from checkmate.lib.models import BaseDocument,DiskProject

class Issue(BaseDocument):

    class Meta(BaseDocument.Meta):
        dbref_includes = ['code',
                          'analyzer',
                          'file_revision.language',
                          'file_revision.path',
                          'file_revision.sha']

    """
    An `Issue` object represents an issue or problem with the code. 
    It can be associated with one or multiple file revisions, code objects etc.
    """
    pass

class Summary(BaseDocument):
    """
    Summary associated with a given snapshot
    """
    pass

class GitFileRevision(BaseDocument):

    """
    issues -> list of issues associated with this file revision
    code objects -> list of code objects associated with this file revision
    """

    class Meta(BaseDocument.Meta):
        dbref_includes = ['path','sha','language']
    
    def get_file_content(self):
        return self.project.eager.repository.get_file_content_by_sha(self.sha)

class GitSnapshot(BaseDocument):

    """
    Problem: Storing all file revisions in all snapshots is inefficient!

    Solution: Store mapping between file revisions and snapshots in M2M table (?)
    """

    FileRevision = GitFileRevision

    class Meta(BaseDocument.Meta):

        dbref_includes = ['sha',
                          'committer_date',
                          'committer_date_ts',
                          'committer_name',
                          'committer_email',
                          'author_date',
                          'author_date_ts',
                          'author_name',
                          'tree_sha',
                          'log'
                          ]

    def initialize(self):
        if not hasattr(self,'file_revisions'):
            self.file_revisions = []

    def get_file_revisions(self,backend):

        file_revisions = list(backend.filter(self.FileRevision,{'pk' : {'$in' : self.file_revisions}}))
        return file_revisions

    def get_git_file_revisions(self,filters = None):

        files = self.project.eager.repository.get_files_in_commit(self.sha)

        if filters:
            for filter_func in filters:
                files = [f for f in files if f['path'] in filter_func([ff['path'] for ff in files])]

        file_revisions = []
        for file_obj in files:
            file_revision = self.FileRevision(file_obj)
            file_revision.project = self.project
            file_revision.fr_pk = file_revision.path+":"+file_revision.sha
            file_revision.pk = uuid.uuid4().hex
            file_revisions.append(file_revision)
        return file_revisions

    def get_diffs(self,snapshot = None):
        return self.project.eager.repository.get_diffs(self.sha,snapshot.sha if snapshot else None)

class GitBranch(BaseDocument):

    class Meta(BaseDocument.Meta):
        collection = "branch"
        dbref_includes = ["project","remote","name"]

class GitProject(DiskProject):

    GitSnapshot = GitSnapshot
    GitBranch = GitBranch

    class Meta(BaseDocument.Meta):
        collection = "project"
    
    def initialize(self):
        if not hasattr(self,'git_snapshots'):
            self.git_snapshots = []

    @property
    def repository(self):
        if not hasattr(self,'_repository'):
            if not hasattr(self,'path'):
                raise Exception("You must specify a file path for the repository!")
            self._repository = Repository(self.path)
        return self._repository

    def get_git_snapshots(self,**kwargs):
        """
        Returns a list of snapshots in a given repository.
        """
        commits = self.repository.get_commits(**kwargs)
        snapshots = []
        for commit in commits:
            snapshot = self.GitSnapshot(commit)
            snapshot.project = self
            snapshot.pk = uuid.uuid4().hex
            snapshots.append(snapshot)
        return snapshots
