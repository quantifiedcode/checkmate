# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from checkmate.lib.analysis.base import BaseAnalyzer

import os
import tempfile
import json
import subprocess

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
                location = (((issue['error']['line'],issue['error']['character']),
                              (issue['error']['line'],None)),)
                issues.append({
                    'code' : issue['error']['code'],
                    'location' : location,
                    'data' : issue['error'],
                    'fingerprint' : self.get_fingerprint_from_code(file_revision,location)
                    })

        finally:
            os.unlink(f.name)
        return {'issues' : issues}
