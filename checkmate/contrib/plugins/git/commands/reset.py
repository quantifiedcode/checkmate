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
import sys
import os
import os.path
import json
import time

from checkmate.management.commands.reset import Command as ResetCommand

class Command(ResetCommand):

    def get_snapshots(self):
        snapshots = self.backend.filter(self.project.GitSnapshot,{'project.pk' : self.project.pk})
        return snapshots

    def get_file_revisions(self,snapshots):
        file_revisions = self.backend.filter(self.project.GitSnapshot.FileRevision,{'project.pk' : self.project.pk})
        return file_revisions

    def get_branches(self):
        branches = self.backend.filter(self.project.GitBranch,{'project.pk' : self.project.pk})
        return branches

    def run(self):
        super(Command,self).run()

        branches = self.get_branches()
        print "Deleting %s branches" % len(branches)
        branches.delete()
        self.backend.commit()


