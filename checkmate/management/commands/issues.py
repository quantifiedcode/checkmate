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
"""

"""

import logging

logger = logging.getLogger(__name__)

from checkmate.management.commands.base import BaseCommand

class Command(BaseCommand):

    """
    Returns a list of issues for the current snapshot or file revision.
    """

    def run(self):
        print self.opts
        print self.extra_args
        snapshot_pk = None
        filenames = None
        if self.extra_args:
            if len(self.extra_args) == 1:
                snapshot_pk = self.extra_args[0]
            else:
                snapshot_pk,filenames = self.extra_args[0],self.extra_args[1:]
        print snapshot_pk,filenames

        if snapshot_pk:
            try:
                snapshot = self.backend.get(self.project.DiskSnapshot,
                                            {'pk' : {'$regex' : r'^'+snapshot_pk}})
            except self.project.DiskSnapshot.DoesNotExist:
                logger.error("Snapshot %s does not exist!" % snapshot_pk)
                return -1
            except self.project.DiskSnapshot.MultipleDocumentsReturned:
                logger.error("Ambiguous key %s!" % snapshot_pk)
                return -1
        else:
            try:
                snapshot = self.backend.filter(self.project.DiskSnapshot,{})\
                                       .sort('created_at',-1)[0]
            except IndexError:
                logger.error("No snapshots in this project.")
                return -1
        issues = self.backend.filter(self.project.Issue,
                                     {'file_revision.pk' : {'$in' : snapshot.file_revisions}})\
                             .sort('analyzer',1)
        
        for issue in issues:
            print "%(analyzer)s\t%(code)s\t" % {'analyzer' : issue['analyzer'],
                                                'code' : issue['code']}