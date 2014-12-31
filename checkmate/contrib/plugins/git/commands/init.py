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
from checkmate.management.helpers import save_project_config
from checkmate.management.commands.init import Command as InitCommand

import sys
import os
import os.path
import json
import time
import uuid
import logging

logger = logging.getLogger(__name__)

"""
Creates a new git project. The command proceeds as follows:

-We look for a git project in the current directory tree.
-If we find one, we create the .checkmate directory in the top-level directory of the repository.
-If a project already exists in the same directory, we do nothing.
"""

class Command(InitCommand):

    requires_valid_project = False

    options = InitCommand.options + []

    description = """
    Initializes a new checkmate project.
    """

    def _search_for_git_project(self,path = None):
        if not path:
            path = os.getcwd()
        while path != "/":
            files = os.listdir(path)
            if ".git" in files and os.path.isdir(os.path.join(path,".git")):
                return path
            path = os.path.dirname(path)
        return None 

    def run(self):
        logger.info("Initializing new project")
        git_path = self._search_for_git_project()
        if git_path:
            config_path = git_path+"/.checkmate"
            project_path = git_path
        else:
            return -1
        if os.path.exists(config_path):
            logger.error("Found another project with the same path, aborting.")
            return -1

        if not self.opts['backend'] in ('file','mongo'):
            logger.error("Unknown backend: %s" % args.backend)
            return -1

        config = {
            'project_id' : uuid.uuid4().hex if not self.opts['pk'] else self.opts['pk'],
            'project_class' : 'GitProject',
            'backend' : {
                'driver' : self.opts['backend'],
            }
        }

        self.configure_backend(config)

        os.makedirs(config_path)
        save_project_config(config_path,config)
