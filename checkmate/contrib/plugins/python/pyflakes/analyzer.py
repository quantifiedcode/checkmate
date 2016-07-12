# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import ast
import os.path
import sys
import os
import checkmate.settings as settings
import hashlib

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
        for issue in reporter._issues:
            if not issue.get('fingerprint'):
                issue['fingerprint'] = self.get_fingerprint_from_code(file_revision,issue['location'])
        return {'issues' : reporter._issues}

class Reporter(BaseReporter):

    def __init__(self,*args,**kwargs):
        super(Reporter,self).__init__(*args,**kwargs)
        self._issues = []

    def unexpectedError(self,filename,msg):
        issue = {
            'code' : '0000',
            'data' : {'description' : unicode(msg,errors='ignore')},
            'location' : (),
            'fingerprint' : hashlib.sha1(msg).hexdigest()
        }
        self._issues.append(issue)

    def syntaxError(self,filename,msg,lineno,offset,text):
        location = (((lineno,offset),(lineno,None)),)
        issue = {
            'code' : '0001',
            'type' : 'syntax error',
            'level' : 'error',
            'data' : {'description' : unicode(msg,errors='ignore'),'text' : unicode(text,errors='ignore')},
            'location' : location,
        }
        self._issues.append(issue)

    def flake(self,warning):
        location = (((warning.lineno,warning.col),(warning.lineno,None)),)
        issue = {
            'code' : warning.__class__.__name__,
            'data' : {'description' : (warning.message % warning.message_args)},
            'location' : location,
        }
        if len(self._issues) > 100:
            if self._issues[-1]['code'] != 'TooManyIssues':
                issue = {
                    'code' : 'TooManyIssues',
                    'data' : {},
                    'fingerprint' : hashlib.sha1('TooManyIssues').hexdigest()
                }
            else:
                return

        self._issues.append(issue)
