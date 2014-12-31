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

from blitzdb import Document

import os
import uuid
import time
import datetime
import logging

logger = logging.getLogger(__name__)

class BaseDocument(Document):

    def pre_save(self):
        if not 'created_at' in self:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

class CodeObject(BaseDocument):

    class Meta(Document.Meta):
        dbref_includes = ['node_type','language','name']

class IssueClass(BaseDocument):

    """
    Describes a user-specific issue class.
    """

    class Meta(Document.Meta):
        dbref_includes = ['code','analyzer','language','title','url']


class Issue(BaseDocument):

    class Meta(Document.Meta):
        dbref_includes = ['code','analyzer','file_revision.language','file_revision.path','file_revision.sha']

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

class MockFileRevision(BaseDocument):

    def get_file_content(self):
        return self.code

class DiskFileRevision(BaseDocument):

    class Meta(Document.Meta):
        dbref_includes = ['path','language']
        collection = "disk_file_revision"

    def get_file_content(self):
        project_path = self.project.eager.path
        file_path = os.path.join(project_path,self.path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path,"rb") as input_file:
                return input_file.read()
        else:
            raise IOError("File does not exist: %s" % file_path)

class DiskSnapshot(BaseDocument):

    FileRevision = DiskFileRevision

    """
    file revisions -> list of file revisions associated with this snapshot
    modified file revisions -> list of modified file revision associated with this snapshot
    new file revisions -> list of new file revisions associated with this snapshot
    """

    class Meta(Document.Meta):

        pass

    def get_diffs(self,my_file_revisions,other_file_revisions = None):
        if not other_file_revisions:
            return [('A',fr.path) for fr in my_file_revisions]
        else:
            my_file_revisions_dict = dict([(fr.path,fr) for fr in my_file_revisions])
            other_file_revisions_dict = dict([(fr.path,fr) for fr in other_file_revisions])

            diffs = []

            my_file_paths = set(my_file_revisions_dict.keys())
            other_file_paths = set(other_file_revisions_dict.keys())

            diffs += [('A',fn) for fn in my_file_paths - other_file_paths]
            diffs += [('D',fn) for fn in other_file_paths - my_file_paths]
            diffs += [('M',fn) for fn in (my_file_paths & other_file_paths) \
                        if my_file_revisions_dict[fn].file_stats['mtime'] > \
                           other_file_revisions_dict[fn].file_stats['mtime']
                     ]

        return diffs

class DiskProject(BaseDocument):

    DiskSnapshot = DiskSnapshot
    CodeObject = CodeObject
    Summary = Summary
    Issue = Issue

    class Meta(Document.Meta):
        collection = "project"
    
    def initialize(self):
        if not hasattr(self,'disk_snapshots'):
            self.disk_snapshots = []

    def get_disk_file_revisions(self,file_filters = [],path_filters = []):

        all_filenames = []

        def apply_filters(filenames_or_paths,filters):
            filtered_filenames_or_paths = filenames_or_paths[:]
            for filter_function in filters:
                filtered_filenames_or_paths = filter_function(filtered_filenames_or_paths)
            return filtered_filenames_or_paths

        def check_directory(path):
            filenames = os.listdir(path)
            base_path = os.path.commonprefix([path,self.path])
            rel_filenames = [os.path.relpath(os.path.join(path,filename),self.path) 
                             for filename in filenames]

            filenames_to_add = []
            paths_to_explore = []

            for rel_path in rel_filenames:
                full_path = os.path.join(base_path,rel_path)
                if os.path.isfile(full_path):
                    filenames_to_add.append(rel_path)
                elif os.path.isdir(full_path):
                    paths_to_explore.append(rel_path)

            all_filenames.extend(apply_filters(filenames_to_add,file_filters))
            paths_to_explore = apply_filters(paths_to_explore,path_filters)

            for path in paths_to_explore:
                check_directory(os.path.join(base_path,path))

        check_directory(self.path)

        file_revisions = []
        for filename in all_filenames:
            file_revision = self.DiskSnapshot.FileRevision()
            file_path = os.path.join(self.path,filename)
            try:
                file_revision.file_stats = dict(zip(('mode',
                                                     'inode',
                                                     'device',
                                                     'nlink',
                                                     'uid',
                                                     'gid',
                                                     'size',
                                                     'atime',
                                                     'mtime',
                                                     'ctime')
                                                    ,os.stat(file_path)))
            except:
                logger.warning("Cannot stat %s, skipping..." % file_path)
                continue
            file_revision.path = filename.decode("utf-8")
            file_revision.fr_pk = file_revision.path+u":"+u"%d" % file_revision.file_stats['mtime']
            file_revision.pk = uuid.uuid4().hex
            file_revision.project = self
            file_revisions.append(file_revision)

        return file_revisions
