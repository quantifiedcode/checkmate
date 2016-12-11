# -*- coding: utf-8 -*-

from __future__ import unicode_literals
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
    Initializes a new git checkmate project. Requires an initialized checkmate project.
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

        if self.opts.get('git_path'):
            git_path = self.opts['git_path']
        else:
            git_path = self.find_git_repository(project_path)

        if git_path is None:
            logger.error("No git project found!")
            return -1

        try:
            repo = self.backend.get(GitRepository,{'project' : self.project})
        except GitRepository.DoesNotExist:
            repo = GitRepository({'project' : self.project})

        repo.path = project_path

        with self.backend.transaction():
            self.backend.save(repo)
