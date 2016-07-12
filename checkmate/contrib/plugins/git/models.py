# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid
import time
import datetime
import logging
import copy
import traceback

logger = logging.getLogger(__name__)

from blitzdb.fields import (DateTimeField,
                            CharField,
                            IntegerField,
                            ForeignKeyField,
                            EnumField,
                            TextField,
                            ManyToManyField)

from checkmate.lib.models import (Snapshot,
                                  Project,
                                  BaseDocument,
                                  FileRevision,
                                  Diff,
                                  IssueOccurrence)

class GitSnapshot(BaseDocument):

    """
    """

    project = ForeignKeyField('Project',unique = False,backref = 'git_snapshots')
    snapshot = ForeignKeyField('Snapshot',unique = True,backref = 'git_snapshot')
    sha = CharField(indexed = True,length = 40)
    hash = CharField(indexed = True,length = 64)
    committer_date = DateTimeField(indexed = True)
    author_date = DateTimeField(indexed = True)
    author_name = CharField(length = 100)
    committer_date_ts = IntegerField(indexed = True)
    author_date_ts = IntegerField(indexed = True)
    tree_sha = CharField(indexed = True,length = 40)
    log = TextField(indexed = False)

    class Meta(BaseDocument.Meta):

        unique_together = [('project','sha')]

class GitBranch(BaseDocument):

    project = ForeignKeyField('Project',backref = 'git_branches')
    name = CharField(indexed = True,length = 100)
    hash = CharField(indexed = True,length = 64)
    remote = CharField(indexed = True,length = 100)
    last_analyzed_snapshot = ForeignKeyField('GitSnapshot')
    head_snapshot = ForeignKeyField('GitSnapshot')

    class Meta(BaseDocument.Meta):

        unique_together = [('project','name')]
