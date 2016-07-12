# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from base import BaseCommand

import logging
import sys
import os
import os.path
import json
import time

logger = logging.getLogger(__name__)

from checkmate.lib.models import (Snapshot,
                                  FileRevision,
                                  Issue,
                                  IssueOccurrence,
                                  Diff,
                                  DiffIssueOccurrence,
                                  DiffFileRevision)

class Command(BaseCommand):

    def run(self):

        logger.info("Resetting project.")

        backend = self.backend
        project = self.project
        with backend.transaction():
            self.settings.call_hooks('project.reset.before',self.project)
            diffs = self.backend.filter(Diff,{'$or' : [{'project' : self.project},
                                                       {'project' : {'$exists' : False}}]})
            file_revisions = self.backend.filter(FileRevision,{'project' : self.project})
            backend.filter(DiffIssueOccurrence,{'diff' : {'$in' : diffs}}).delete()
            backend.filter(DiffFileRevision,{'file_revision' : {'$in' : file_revisions}}).delete()
            backend.filter(IssueOccurrence,{'file_revision' : {'$in' : file_revisions}}).delete()
            backend.filter(Issue,{'project' : project}).delete()
            diffs.delete()

            logger.info("Deleting %d file revisions" % (len(file_revisions)))
            file_revisions.delete()
            snapshots = backend.filter(Snapshot,{'project' : self.project})
            logger.info("Deleting %d snapshots" % (len(snapshots)))
            snapshots.delete()

            self.settings.call_hooks('project.reset.after',self.project)
        print "Done"
