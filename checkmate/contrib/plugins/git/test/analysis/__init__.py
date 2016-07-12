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

    data_path = os.path.join(os.path.abspath(__file__+"/../../"),"data")
    gzip_filename = "project.tar.gz"

    @classmethod
    def setUpClass(cls):

        cls.tmpdir = tempfile.mkdtemp()
        cls.tmp_project_path = os.path.join(cls.tmpdir,"project")
        subprocess.call(['tar','-xvzf',os.path.join(cls.data_path,cls.gzip_filename)],
                        cwd = cls.tmpdir)

        cls.current_path = os.getcwd()

        cls.settings = Settings(
            analyzers = {
                'test':
                    {
                        'title' : 'Test',
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

        cls.settings.load_plugins()

        os.chdir(cls.tmp_project_path)
        init_command = InitCommand(project=None,settings=cls.settings)
        init_command.run()

        assert os.path.exists(os.path.join(cls.tmp_project_path,'.checkmate'))
        cls.project,cls.backend = get_project_and_backend(cls.tmp_project_path, cls.settings)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.current_path)
        shutil.rmtree(cls.tmpdir)
