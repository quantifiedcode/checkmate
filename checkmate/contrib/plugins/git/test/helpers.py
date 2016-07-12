from unittest import TestCase

from checkmate.management.commands.init import Command as InitCommand

from checkmate.contrib.plugins.git.commands.analyze import Command as AnalyzeCommand
from checkmate.contrib.plugins.git.models import GitSnapshot, GitBranch
from checkmate.lib.models import Issue, IssueOccurrence
from checkmate.lib.analysis import BaseAnalyzer
from checkmate.settings import Settings
from checkmate.management.helpers import get_project_and_backend

import tempfile
import shutil
import os
import pprint
import subprocess
import logging
import traceback

logger = logging.getLogger(__name__)

class ExampleAnalyzer(BaseAnalyzer):

    def analyze(self, file_revision):
        return {
            'issues' : [
                {
                    'code' : 'test',
                    'location' : ( ((0,1),(10,10)), ),
                    'description' : 'foo',
                    'fingerprint' : 'testprint'
                }
            ]
        }

class RepositoryBasedTest(TestCase):

    data_path = os.path.join(os.path.abspath(__file__+"/../"),"data")
    gzip_filename = "project.tar.gz"

    def setUp(self):

        self.tmpdir = tempfile.mkdtemp()
        self.tmp_project_path = os.path.join(self.tmpdir,"project")
        subprocess.call(['tar','-xvzf',os.path.join(self.data_path,self.gzip_filename)],
                        cwd = self.tmpdir)

        self.current_path = os.getcwd()

        self.settings = Settings(
            analyzers = {
                'test':
                    {
                        'title' : 'Example',
                        'class' : ExampleAnalyzer,
                        'language' : 'python',
                        'issues_data' : {},
                    },
            },
            aggregators = {},
            models = None,
            commands = {},
            plugins = {
                'git' : 'checkmate.contrib.plugins.git'
            }
        )

        self.settings.load_plugins()

        os.chdir(self.tmp_project_path)
        init_command = InitCommand(project=None,settings=self.settings)
        init_command.run()

        assert os.path.exists(os.path.join(self.tmp_project_path,'.checkmate'))
        self.project,self.backend = get_project_and_backend(self.tmp_project_path, self.settings)

    def tearDown(self):
        os.chdir(self.current_path)
        shutil.rmtree(self.tmpdir)
