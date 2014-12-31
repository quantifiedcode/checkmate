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
from base import BaseCommand
from checkmate.management.helpers import save_project_config

import sys
import os
import os.path
import json
import time
import uuid
import logging

logger = logging.getLogger(__name__)

"""
Creates a new project. The command proceeds as follows:

-We create a .checkmate directory in the current directory.
-If a project already exists in the same directory, we do nothing.
"""

class Command(BaseCommand):

    requires_valid_project = False

    options = BaseCommand.options + [
        {
        'name'        : '--backend',
        'action'      : 'store',
        'dest'        : 'backend',
        'type'        : str,
        'default'     : 'file',
        'help'        : 'The backend to use.'
        },
        {
        'name'        : '--backend-opts',
        'action'      : 'store',
        'dest'        : 'backend_opts',
        'type'        : str,
        'default'     : '',
        'help'        : 'Backend options (e.g. connection string).'
        },
        {
        'name'        : '--path',
        'action'      : 'store',
        'dest'        : 'path',
        'default'     : None,
        'type'        : str,
        'help'        : 'The path where to create a new project (default: current working directory)'
        },
        {
        'name'        : '--pk',
        'action'      : 'store',
        'dest'        : 'pk',
        'type'        : str,
        'default'     : None,
        'help'        : 'The primary key to use for the project',
        }]

    description = """
    Initializes a new checkmate project.
    """

    def configure_backend(self,config):
        if self.opts['backend_opts']:
            backend_opts = dict([s.split("=") for s in self.opts['backend_opts'].split(",")])
            if self.opts['backend'] == 'mongo':
                if not 'db' in backend_opts:
                    logger.error("Error: 'db' option missing (required for 'mongo' backend)!\n")
                    return -1
            for key,value in backend_opts.items():
                if not key in config['backend']:
                    config['backend'][key] = value

    def run(self):
        logger.info("Initializing new disk-based project in the current directory.")

        project_path = self.opts['path'] or os.getcwd()
        config_path = project_path+"/.checkmate"

        if os.path.exists(config_path):
            logger.error("Found another project with the same path, aborting.")
            return -1

        if not self.opts['backend'] in ('file','mongo'):
            logger.error("Unknown backend: %s" % args.backend)
            return -1

        config = {
            'project_id' : uuid.uuid4().hex if not self.opts['pk'] else self.opts['pk'],
            'project_class' : 'DiskProject',
            'backend' : {
                'driver' : self.opts['backend'],
            }
        }

        self.configure_backend(config)

        os.makedirs(config_path)
        save_project_config(config_path,config)
