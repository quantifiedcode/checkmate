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
from base import BaseCommand

import sys
import os
import os.path
import json
import time

class Command(BaseCommand):

    def get_snapshots(self):
        snapshots = self.backend.filter(self.project.DiskSnapshot,{'project.pk' : self.project.pk})
        return snapshots

    def get_file_revisions(self,snapshots):
        file_revisions = self.backend.filter(self.project.DiskSnapshot.FileRevision,{'project.pk' : self.project.pk})
        return file_revisions

    def run(self):

        print "Resetting project."

        backend = self.backend
        project = self.project
        snapshots = self.get_snapshots()
        snapshots_list = list(snapshots)
        file_revisions = self.get_file_revisions(snapshots)
        file_revisions_list = list(file_revisions)

        for cls in [self.project.Summary,self.project.Issue,self.project.CodeObject]:
            objs = backend.filter(cls,{'file_revision.pk' : {'$in' : [fr.pk for fr in file_revisions_list]}})
            print "Deleting %d objects of type %s " % (len(objs),cls.__name__)
            objs.delete()
            backend.commit()

        print "Deleting %d file revisions" % (len(file_revisions_list))
        file_revisions.delete()
        backend.commit()

        print "Deleting %d snapshots" % (len(snapshots_list))
        snapshots.delete()
        backend.commit()
