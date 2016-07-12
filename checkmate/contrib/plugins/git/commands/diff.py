# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from .base import Command as BaseCommand
from ..models import GitSnapshot,GitBranch
from checkmate.lib.code import CodeEnvironment
from checkmate.lib.models import Diff
from ..lib.repository import group_snapshots_by_date,get_first_date_for_group

import sys
import os
import random
import os.path
import json
import time
import pprint
import logging
import calendar
import datetime
import textwrap

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    """
    Generates diffs between snapshots of a given project.

    You can specify a diff group (e.g. "sequential") and a key (e.g "last_analysis") which will
    be used to filter the returned diffs.
    """

    options = BaseCommand.options + [
        {
        'name'        : '--branch',
        'action'      : 'store',
        'dest'        : 'branch',
        'type'        : str,
        'default'     : 'master',
        'help'        : 'The branch for which to generate the diffs.'
        },
        {
        'name'        : '--type',
        'action'      : 'store',
        'dest'        : 'type',
        'type'        : str,
        'default'     : '',
        'help'        : 'The type of the diffs to generate.'
        },
        {
        'name'        : '--offset',
        'action'      : 'store',
        'dest'        : 'offset',
        'type'        : int,
        'default'     : 0,
        'help'        : 'The offset from the latest snapshot.'
        },
        {
        'name'        : '--from',
        'action'      : 'store',
        'dest'        : 'from',
        'type'        : str,
        'default'     : '',
        'help'        : 'The date for which to generate the diff.'
        },
        {
        'name'        : '--key',
        'action'      : 'store',
        'dest'        : 'key',
        'type'        : str,
        'default'     : '',
        'help'        : 'The key (e.g. sequential, monthly, weekly, daily).'
        },
        ]

    @classmethod
    def serialize(cls,result,fmt = 'json'):
        if fmt == 'text':
            d = {
                'sha_a' : result.snapshot_a.git_snapshot.sha[:8],
                'sha_b' : result.snapshot_b.git_snapshot.sha[:8],
                'date_a' : result.snapshot_a.git_snapshot.committer_date,
                'date_b' : result.snapshot_b.git_snapshot.committer_date,
            }
            s = textwrap.dedent("""
            Diff between commit {sha_a} ({date_a}) and {sha_b} ({date_b})

            """.format(**d))
            return s
        elif fmt == 'json':
            return json.dumps(self.backend.serialize(result),indent = 2)

    def run(self):

        if not self.opts['branch']:
            branch_name = self.project.git.get_default_branch()
        else:
            branch_name = self.opts['branch']
        try:
            branch = self.backend.get(GitBranch,
                                      {'project.pk' : self.project.pk,'name' : branch_name })
            diffs = []
        except GitBranch.DoesNotExist:
            raise self.CommandException("Cannot load branch %s" % branch_name)

        if self.opts['type'] == 'last_analysis':
            if not branch.get('last_analyzed_snapshot'):
                raise self.CommandException("No data about last analyzed snapshot available for branch %s" % branch_name)
            git_snapshot_a = branch.last_analyzed_snapshot.eager
            if not 'head_snapshot' in branch:
                raise self.CommandException("No data about head snapshot available for branch %s" % branch_name)
            git_snapshot_b = branch.head_snapshot.eager
            if git_snapshot_a['sha'] == git_snapshot_b['sha']:
                raise self.CommandException("No changes since last analysis!")
        elif self.opts['type'] in ('weekly','daily','monthly'):
            if self.opts['from']:
                if isinstance(self.opts['from'],(str,unicode)):
                    try:
                        from_date = datetime.datetime.strptime(self.opts['from'],"%Y-%m-%d")
                    except ValueError:
                        raise self.CommandException("Invalid date format or value for `from` parameter (use YYYY-mm-dd)")
            else:
                try:
                    from_date = self.project.git.get_snapshots(branch = branch_name,limit = 1)[0]\
                            .committer_date + datetime.timedelta(days = 1)
                except IndexError:
                    raise self.CommandException("No snapshots on branch %s" % branch_name)

            dt = get_first_date_for_group(from_date,self.opts['type'],1+self.opts['offset'])

            if self.opts['type'] == 'daily':
                deltat = datetime.timedelta(days = 1)
            elif self.opts['type'] == 'weekly':
                deltat = datetime.timedelta(days = 7)
            elif self.opts['type'] == 'monthly':
                deltat = datetime.timedelta(days = calendar.monthrange(dt.year,dt.month)[1])

            snapshots = self.project.git.get_snapshots(branch = branch_name,
                                                       since = dt.ctime(),
                                                       until = (dt+deltat).ctime())
            if not snapshots:
                raise self.CommandException("No snapshots on branch %s" % branch_name)
            grouped_snapshots = group_snapshots_by_date(snapshots,self.opts['type'])
            snapshots_list = grouped_snapshots.values()[0]
            sha_a,sha_b = snapshots_list[0]['sha'],snapshots_list[-1]['sha']
            try:
                git_snapshot_a = self.backend.get(GitSnapshot,{'sha' : sha_a,
                                                               'snapshot.project' : self.project})
            except GitSnapshot.DoesNotExist:
                raise self.CommandException("Unknown snapshot: %s" % sha_a)
            try:
                git_snapshot_b = self.backend.get(GitSnapshot,{'sha' : sha_b,
                                                               'snapshot.project' : self.project})
            except GitSnapshot.DoesNotExist:
                raise self.CommandException("Unknown snapshot: %s" % sha_b)

        else:
            if len(self.extra_args) != 2:
                raise self.CommandException("You need to specify exactly two commit SHAs to be diffed!")
            sha_a,sha_b = self.extra_args
            try:
                git_snapshot_a = self.backend.get(GitSnapshot,{'sha' : sha_a,
                                                               'snapshot.project' : self.project})
            except GitSnapshot.DoesNotExist:
                raise self.CommandException("Unknown snapshot: %s" % sha_a)
            try:
                git_snapshot_b = self.backend.get(GitSnapshot,{'sha' : sha_b,
                                                               'snapshot.project' : self.project})
            except GitSnapshot.DoesNotExist:
                raise self.CommandException("Unknown snapshot: %s" % sha_b)

        #We generate the diff, or fetch it from the database in case it already exists.
        if 'settings' in self.opts:
            settings = self.opts['settings']
        else:
            settings = self.project.get('settings',{})
        try:
            diff = self.backend.get(Diff,{'snapshot_a' : git_snapshot_a.snapshot,
                                          'snapshot_b' : git_snapshot_b.snapshot})
        except Diff.DoesNotExist:
            code_environment = CodeEnvironment(self.project, [], settings=settings)

            diff,diff_file_revisions,diff_issue_occurrences = code_environment.diff_snapshots(git_snapshot_a.snapshot, git_snapshot_b.snapshot,save = True)

        return diff
