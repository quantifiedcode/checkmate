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
import ast
import os.path
import sys
import os
import checkmate.settings as settings

from checkmate.lib.stats.helpers import directory_splitter
from checkmate.lib.analysis.base import BaseAnalyzer
from pyflakes.reporter import Reporter as BaseReporter
from pyflakes.api import check as pyflakes_check

class PyFlakesAnalyzer(BaseAnalyzer):

    def summarize(self,items):

        stats = {
            'n_errors' : sum([item['stats']['n_errors'] for item in items if 'stats' in item]),
        }

        return stats

    def analyze(self,file_revision):
        null = open(os.devnull,"w")
        reporter = Reporter(null,null)
        pyflakes_check(file_revision.get_file_content(),file_revision.path,reporter)
        return {'issues' : reporter._issues}

class Reporter(BaseReporter):

    def __init__(self,*args,**kwargs):
        super(Reporter,self).__init__(*args,**kwargs)
        self._issues = []

    def unexpectedError(self,filename,msg):
        issue = {
            'code' : '0000',
            'data' : {'description' : msg},
            'location' : (),
        }
        self._issues.append(issue)

    def syntaxError(self,filename,msg,lineno,offset,text):
        issue = {
            'code' : '0001',
            'type' : 'syntax error',
            'level' : 'error',
            'data' : {'description' : msg,'text' : text},
            'location' : (((lineno,offset),(lineno,None)),),
        }
        self._issues.append(issue)

    def flake(self,warning):
        issue = {
            'code' : warning.__class__.__name__,
            'data' : {'description' : (warning.message % warning.message_args)},
            'location' : (((warning.lineno,warning.col),(warning.lineno,None)),),
        }
        if len(self._issues) > 1000:
            raise ValueError("Too many issues in file, bailing out!")
        self._issues.append(issue)

