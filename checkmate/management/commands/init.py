# -*- coding: utf-8 -*-

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
        'default'     : 'sql',
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

    def run(self):
        logger.info("Initializing new project in the current directory.")

        project_path = self.opts['path'] or os.getcwd()
        config_path = project_path+"/.checkmate"

        if os.path.exists(config_path):
            logger.error("Found another project with the same path, aborting.")
            return -1

        if not self.opts['backend'] in ('sql'):
            logger.error("Unsupported backend: %s" % self.opts['backend'])
            return -1

        config = {
            'project_id' : uuid.uuid4().hex if not self.opts['pk'] else self.opts['pk'],
            'project_class' : 'Project',
            'backend' : {
                'driver' : self.opts['backend'],
            }
        }

        os.makedirs(config_path)
        save_project_config(project_path,config)
