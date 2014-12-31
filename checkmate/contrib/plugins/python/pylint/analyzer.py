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
from pylint.lint import PyLinter
from astroid import MANAGER, AstroidBuildingException
from pylint.reporters import BaseReporter
from astroid.builder import AstroidBuilder

import StringIO
import traceback
import tokenize
import tempfile
import sys
import os

from checkmate.lib.analysis.base import BaseAnalyzer

class PyLintAnalyzer(BaseAnalyzer):

    def diff(self,results_a,results_b):
        pass

    def diff_summary(self,summary_a,summary_b):
        pass

    def summarize(self,items):

        stats = {
            'average_global_note' : 0,
            'n_warnings' : 0,
            'n_errors' : 0,
        }
        cnt = 0
        for item in [item['stats'] for item in items if 'stats' in item]:
            if 'global_note' in item:
                cnt+=1
                stats['average_global_note']+=item['global_note']
            if 'n_warnings' in item:
                stats['n_warnings']+=item['n_warnings']
            if 'n_errors' in item:
                stats['n_errors']+=item['n_errors']

        if cnt > 0:
            stats['average_global_note']/=float(cnt)
        else:
            del stats['average_global_note']

        return stats

    def analyze(self,file_revision):
        try:
            reporter = Reporter()
            linter = Linter(reporter = reporter)
            linter.load_default_plugins()
            for unsafe_checker in ['logging','stdlib']:
                if unsafe_checker in linter._checkers:
                    del linter._checkers[unsafe_checker]
            with open(os.devnull,"w") as devnull:
                #pylint will print a lot of garbage when it fails, so we redirect all output to dev/null
                try:
                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    sys.stdout = devnull
                    sys.stderr = devnull
                    linter.check(file_revision.get_file_content(),file_revision.path)
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
            stats = linter.stats
            stats['by_msg'] = stats['by_msg'].items()
            if 'dependencies' in stats:
                del stats['dependencies']
            sanitized_stats = {}
            for key,value in stats.items():
                sanitized_stats[key] = value.items() if isinstance(value,dict) \
                    else list(value) if isinstance(value,set) else value
            issues = reporter.get_issues()
            return {'stats':sanitized_stats,'issues':issues}
        except KeyboardInterrupt:
            raise
        except ImportError:
            pass
        except:
            raise
        
class Reporter(BaseReporter):

    """
    We reimplement the add_message function and store all incoming messages in a list.
    """

    def __init__(self,*args,**kwargs):
        super(Reporter,self).__init__(*args,**kwargs)
        self._messages = []

    def add_message(self, msg_id, location, msg):
        """Client API to send a message"""
        if len(self._messages) > 1000:
            raise ValueError("Too many issues in file, bailing out!")
        self._messages.append((msg_id,location,msg))

    def get_issues(self):
        issues = []

        for msg_id,location,msg in self._messages:
            (filename,filepath,module,line_number,offset) = location

            if msg_id.strip()[0] == 'E':
                issue_level = 'error'
            else:
                issue_level = 'warning'

            issue = {
                'code' : msg_id,
                'data' : {
                    'description' : msg,
                },
                'location' : (((line_number,offset),(line_number,None)),),
            }

            issues.append(issue)

        return issues


    def _display(self,layout):
        pass

class Linter(PyLinter):

    """
    Modified version of PyLinter, which accepts a string and a filename as input and
    analyzes it using the base class. 
    """

    def check(self,content,filename):
        self._content = content
        f = tempfile.NamedTemporaryFile(delete = False)
        try:
            with f:
                f.write(content)
            return super(Linter,self).check([f.name])
        finally:
            os.unlink(f.name)
