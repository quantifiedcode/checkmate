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
from checkmate.management.commands.base import BaseCommand
from ..models import GitSnapshot

import sys
import os
import random
import os.path
import json
import time

class Command(BaseCommand):

    options = BaseCommand.options + [
        {
        'name'        : '--branch',
        'action'      : 'store',
        'dest'        : 'branch',
        'type'        : str,
        'default'     : 'master',
        'help'        : 'The branch for which to show the log.'
        },
        ]

    def run(self):

        if not self.opts['branch']:
            branch = self.project.repository.get_branches()[0]
        else:
            branch = self.opts['branch']

        snapshots = self.backend.filter(GitSnapshot,{'project' : self.project}).sort('committer_date_ts',-1)
        print len(snapshots)
        for snapshot in snapshots:
            print snapshot.committer_date,"  ",snapshot.pk
