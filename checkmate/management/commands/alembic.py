# -*- coding: utf-8 -*-

from __future__ import unicode_literals,absolute_import

from .base import BaseCommand
from checkmate.management.helpers import save_project_config

import os
import logging

logger = logging.getLogger(__name__)

"""
Creates a new project. The command proceeds as follows:

-We create a .checkmate directory in the current directory.
-If a project already exists in the same directory, we do nothing.
"""

from alembic.config import Config,main
from checkmate.settings import project_path

class Command(BaseCommand):

    options = BaseCommand.options

    description = """
    Run Alembic migrations on a projet
    """

    def run(self):
        alembic_cfg = Config(os.path.join(project_path,"alembic.ini"))
        main(argv = self.raw_args)
