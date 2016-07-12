from unittest import TestCase

from checkmate.management.commands.init import Command as InitCommand
from checkmate.management.helpers import get_project_and_backend
from checkmate.settings import Settings

import tempfile
import shutil
import os

class ProjectBasedTest(TestCase):

    def setUp(self):

        self.tmpdir = tempfile.mkdtemp()
        self.tmp_project_path = os.path.join(self.tmpdir,"basic_project")
        os.makedirs(self.tmp_project_path)

        self.settings = Settings(
            analyzers = {},
            aggregators = {},
            commands = {},
            plugins = {
                'git' : 'checkmate.contrib.plugins.git'
            }
        )

        self.settings.load_plugins()
        self.current_path = os.getcwd()

        os.chdir(self.tmp_project_path)
        init_command = InitCommand(None,None)
        init_command.run()

        assert os.path.exists(os.path.join(self.tmp_project_path,'.checkmate'))

        self.project,self.backend = get_project_and_backend(self.tmp_project_path,self.settings)

    def tearDown(self):
        os.chdir(self.current_path)
        shutil.rmtree(self.tmpdir)
