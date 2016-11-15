# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from base import BaseCommand
from checkmate.management.commands.init import Command as BaseCommand
from checkmate.management.helpers import (get_project_config,
                                          get_project,
                                          get_backend)
import sys
import os
import os.path
import json
import time
import uuid
import logging

from ..models import GitRepository

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    description = """
    Initializes a new git checkmate project.
    """

    def find_git_repository(self, path):
        """
        Tries to find a directory with a .git repository
        """
        while path is not None:
            git_path = os.path.join(path,'.git')
            if os.path.exists(git_path) and os.path.isdir(git_path):
                return path
            path = os.path.dirname(path)
        return None

    def run(self):

        project_path = self.opts['path'] or os.getcwd()

        if opts.get('git_path'):
            git_path = opts['git_path']
        else:
            git_path = self.find_git_repository(project_path)

        if git_path is None:
            logger.error("No git project found!")
            return -1

        project_config = get_project_config(project_path)
        backend = get_backend(project_path, project_config, self.settings)
        project = get_project(project_path, project_config, self.settings, backend)

        repo = GitRepository({
            'project' : project,
            'path' : project_path
        })

        with backend.transaction():
            backend.save(repo)
