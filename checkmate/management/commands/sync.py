# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from base import BaseCommand

from collections import defaultdict

import sys
import os
import random
import os.path
import copy
import json
import time
import pprint
import hashlib
import logging

logger = logging.getLogger(__name__)

from checkmate.lib.code import CodeEnvironment
from checkmate.helpers.issue import group_issues_by_fingerprint
from checkmate.lib.models import Snapshot,FileRevision,Issue,IssueOccurrence

class Command(BaseCommand):

    """
    Synchronizes the following objects with an external backend:

    * Snapshot (+FileRevisions) <- needs a unique ID
    * Diff (+FileRevisions) <- needs a unique ID
    * FileRevision () <- needs a unique ID
    * Issue <- needs a unique ID (analyzer, code, fingerprint)
    * IssueOccurrence (+Issue,FileRevision) (issue.id, file_revision.id, )
    * eventually other models from plugin (e.g. GitSnapshot, GitBranch)

    Strategy:

    * First, for all objects send a list with (pk, updated_at) values to the server
    * The server responds with a list of unknown/outdated objects
    * The client send these objects to the server, where they are imported
    * The import order should always match the dependencies between the models (i.e. first FileRevision objects, then Snapshot, then Diff objects)

    The server will check for primary key conflicts and might mingle/alter the PK values of the entities

    Maybe it would be a better strategy to define unique identifiers for each object, which the server can use for checking.

    * Snapshot (sha/...)
    * Diff (snapshot_a.id, snapshot_b.id)
    * FileRevision: (fr_pk)
    * Issue (analyzer, code, fingerprint)
    * IssueOccurrence (issue.id, file_revision.id, from_row, from_col, to_row, to_col, sequence)
    * Snapshot:
    """

    def run(self):

        settings = self.project.settings

        logger.info("Synchronizing analysis results...")

        """
        1.)
        """
