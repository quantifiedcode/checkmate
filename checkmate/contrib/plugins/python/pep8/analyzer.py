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
from checkmate.lib.stats.mapreduce import MapReducer
from checkmate.lib.stats.helpers import directory_splitter
from checkmate.lib.analysis.base import BaseAnalyzer

import pep8
import tempfile

error_types = {
    'E1' : 'indentation',
    'E2' : 'whitespace',
    'E3' : 'blank line',
    'E4' : 'import',
    'E5' : 'line length',
    'E6' : 'statement',
    'E9' : 'runtime',
    'W1' : 'indentation warning',
    'W2' : 'whitespace warning',
    'W3' : 'blank line warning',
    'W6' : 'deprecation warning',
}

class Pep8Analyzer(BaseAnalyzer):

    def summarize(self,items):

        stats = {
            'n_warnings' : 0,
            'n_errors' : 0,
        }

        for item in [item['stats'] for item in items if 'stats' in item]:
            stats['n_warnings']+=item['n_warnings']
            stats['n_errors']+=item['n_errors']

        return stats

    def analyze(self,file_revision):
        pep8style = pep8.StyleGuide(quiet = True)
        try:
            handle,temp_filename = tempfile.mkstemp()
            fh = os.fdopen(handle,"wb")
            fh.write(file_revision.get_file_content())
            fh.close()
            pep8style.init_report(Reporter)
            result = pep8style.check_files([temp_filename])
        finally:
            os.unlink(temp_filename)
        return {'issues' : result.issues}

class Reporter(pep8.BaseReport):

    def init_file(self,filename,lines,expected,line_offset):
        pep8.BaseReport.init_file(self,filename,lines,expected,line_offset)

    def error(self,line_number,offset,text,check):

        code = int(text.strip()[1:4])

        if text.strip()[0] == 'E':
            issue_level = 'error'
        else:
            issue_level = 'warning'

        error_code = text.strip()[:2]

        issue = {
            'code' : text.strip()[0]+"%.4d" % code,
            'data' : {'description' : text},
            'location' : (((line_number,offset),(line_number,None)),),
        }

        if len(self._issues) > 1000:
            raise ValueError("Too many issues in file, bailing out!")

        self._issues.append(issue)
        pep8.BaseReport.error(self,line_number,offset,text,check)

    @property
    def issues(self):
        return self._issues

    def __init__(self,*args,**kwargs):
        super(Reporter,self).__init__(*args,**kwargs)
        self._issues = []
        self._errors = []
