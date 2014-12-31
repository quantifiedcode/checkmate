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
from __future__ import absolute_import

import ast
import os.path
import sys
import os
import checkmate.settings as settings
import tempfile
import json
import subprocess

from checkmate.lib.analysis.base import BaseAnalyzer

import tempfile

class JSHintAnalyzer(BaseAnalyzer):

    def summarize(self,items):
        pass

    def analyze(self,file_revision):
        issues = []
        f = tempfile.NamedTemporaryFile(delete = False)
        try:
            with f:
                f.write(file_revision.get_file_content())
            try:
                result = subprocess.check_output(["jshint",
                                                  "--filename",
                                                  file_revision.path,
                                                  "--reporter",
                                                  os.path.join(os.path.abspath(__file__+"/.."),
                                                               'js/json_reporter'),
                                                  f.name])
            except subprocess.CalledProcessError as e:
                if e.returncode == 2:
                    result = e.output
                else:
                    raise
            json_result = json.loads(result)
            for issue in json_result:
                issues.append({
                    'code' : issue['error']['code'],
                    'location' : ((issue['error']['line'],issue['error']['character']),
                                  (issue['error']['line'],None)),
                    'data' : issue
                    })
        finally:
            os.unlink(f.name)
        return {'issues' : issues}
