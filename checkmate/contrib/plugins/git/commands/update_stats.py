# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
from collections import defaultdict

from checkmate.management.commands.base import BaseCommand
from ..models import GitBranch

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def run(self):

        branches = self.backend.filter(GitBranch,{'project.pk' : self.project.pk})

        branches_by_name = dict([(branch.name,branch) for branch in branches])

        if 'default_branch' in self.project and self.project.default_branch in branches_by_name:
            master_branch = branches_by_name[self.project.default_branch]
        elif 'origin/master' in branches_by_name:
            master_branch = branches_by_name['origin/master']
        else:
            logger.warning("No default branch defined for project %s" % self.project.pk)
            return -1

        stats = {
            'contributors' : self.project.git.repository.get_contributors(),
            'branch' : master_branch.name
        }

        stats['n_commits'] = sum([contributor['n_commits'] for contributor in stats['contributors']])

        self.project.stats = stats
        with self.backend.transaction():
            self.backend.save(self.project)
