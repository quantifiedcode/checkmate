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
from checkmate.management.commands.analyze import Command as AnalyzeCommand
from ..lib.repository import group_snapshots_by_date,get_first_date_for_group

import time
import datetime
import logging

from checkmate.lib.code import CodeEnvironment

logger = logging.getLogger(__name__)

class Command(AnalyzeCommand):

    options = AnalyzeCommand.options + [
        {
        'name'        : '--n',
        'action'      : 'store',
        'dest'        : 'n',
        'type'        : int,
        'default'     : 1,
        'help'        : 'The number of snapshots to analyze.'
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
        'name'        : '--shas',
        'action'      : 'store',
        'dest'        : 'shas',
        'type'        : str,
        'default'     : '',
        'help'        : 'A comma-separated list of commit to analyze, identified by their SHAs.'
        },
        {
        'name'        : '--branch',
        'action'      : 'store',
        'dest'        : 'branch',
        'type'        : str,
        'default'     : '',
        'help'        : 'The branch to analyze.'
        },
        {
        'name'        : '--type',
        'action'      : 'store',
        'dest'        : 'type',
        'type'        : str,
        'default'     : '',
        'help'        : 'The type of analysis (latest, monthly, weekly, daily).'
        },
        ]

    def analyze_grouped_snapshots(self,branch,group,grouped_snapshots):
        for key,snapshots in grouped_snapshots.items():
            last_snp,first_snp = snapshots[0],snapshots[-1]
            self.analyze_and_generate_diffs(branch,
                                            [first_snp,last_snp],
                                            [{'group' : group, 
                                              'key' : key,
                                              'snapshot_a' : first_snp.sha,
                                              'snapshot_b' : last_snp.sha}])

    def get_settings(self,branch):
        settings = {}
        if 'settings' in self.project:
            settings.update(self.project.settings)
        if 'settings' in self.opts:
            settings.update(self.opts['settings'])
        return settings

    def analyze_and_generate_diffs(self,branch,snapshots,diff_list):

        analyzed_snapshots = {}

        for snapshot in snapshots:
            try:
                query = {'sha' : snapshot.sha,'project.pk' : self.project.pk,'analyzed' : True}
                snapshot = self.backend.get(self.project.GitSnapshot,query)
                analyze_snapshot = False
            except self.project.GitSnapshot.DoesNotExist:
                analyze_snapshot = True
            except self.project.GitSnapshot.MultipleDocumentsReturned:
                self.backend.filter(self.project.GitSnapshot,query).delete()
                analyze_snapshot = True

            file_revisions = snapshot.get_git_file_revisions()

            code_environment = CodeEnvironment(file_revisions,settings = self.get_settings(branch))

            if analyze_snapshot:
                snapshot = self.analyze_snapshot(snapshot,
                                                 code_environment,
                                                 save_if_empty = True)

            analyzed_snapshots[snapshot.sha] = snapshot

            self.update_branch(branch,analyzed_snapshots)

        snapshot_pairs = [[analyzed_snapshots[diff_params['snapshot_a']],
                           analyzed_snapshots[diff_params['snapshot_b']]] 
                           for diff_params in diff_list]

        code_environment = CodeEnvironment([])

        diffs = self.generate_diffs(code_environment,snapshot_pairs)

        for diff,snapshot_pair in zip(diffs,snapshot_pairs):
            snapshot_a,snapshot_b = snapshot_pair
            snapshot_b['diff'] = {'snapshot' : snapshot_a,
                                  'issues' : diff['issues'],
                                  'file_revisions' : diff['file_revisions']}
            self.backend.save(snapshot_b)
            self.backend.commit()

        self.backend.commit()

        return analyzed_snapshots

    def update_branch(self,branch_name,snapshots):

        logger.info("Updating info for branch %s" % branch_name)

        branch = self.project.GitBranch({'project' : self.project,
                                      'name' : branch_name,
                                      'snapshots' : [] })

        try:
            branch = self.backend.get(self.project.GitBranch,
                                      {'project.pk' : self.project.pk,'name' : branch_name})
        except self.project.GitBranch.DoesNotExist:
            pass
        except self.project.GitBranch.MultipleDocumentsReturned:
            self.backend.filter(self.project.GitBranch,{'project.pk' : self.project.pk,
                                                     'name' : branch_name}).delete()

        for sha,snapshot in snapshots.items():
            if not sha in branch.snapshots:
                branch.snapshots.append(sha)

        self.backend.save(branch)
        self.backend.commit()

    def run(self):

        if not self.opts['branch']:
            branches = self.project.repository.get_branches()
            if 'default_branch' in self.project and self.project.default_branch in branches:
                branch = self.project_default_branch
            elif 'origin/master' in branches:
                branch = 'origin/master'
            else:
                branch = branches[0]
        else:
            branch = self.opts['branch']

        if self.opts['type'] in ('monthly','weekly','daily'):

            logger.info("Analyzing %d %s commits in branch %s (offset: %d)" % 
                (self.opts['n'],self.opts['type'],branch,self.opts['offset']))

            from_date = self.project.get_git_snapshots(branch = branch,limit = 1)[0]\
                        .committer_date + datetime.timedelta(days = 1)

            dt = get_first_date_for_group(from_date,self.opts['type'],self.opts['n']+\
                 self.opts['offset'])
            snapshots = self.project.get_git_snapshots(branch = branch,
                                                       since = dt.ctime())[:-self.opts['offset'] 
                                                       if self.opts['offset'] != 0 else None]

            grouped_snapshots = group_snapshots_by_date(snapshots)

            self.analyze_grouped_snapshots(branch,self.opts['type'],
                                           grouped_snapshots[self.opts['type']])
        else:
            if self.opts['shas']:
                logger.info("Analyzing %d snapshots" % len(self.opts['shas'].split(",")))
                shas = self.opts['shas'].split(",")
                snapshots_to_analyze = self.project.get_git_snapshots(branch = branch,shas = shas)
            else:
                logger.info("Analyzing the %d most recent commits in branch %s (offset: %d)" % 
                    (self.opts['n'],branch,self.opts['offset']))
                if self.opts['n'] == 0:
                    snapshots_to_analyze = self.project.get_git_snapshots(branch = branch)[::-1]
                else:
                    snapshots_to_analyze = self.project.get_git_snapshots(branch = branch,
                        limit = self.opts['n'],offset = self.opts['offset'])[::-1]
            try:

                def timestamp(dt):
                    return (dt-datetime.datetime(1970,1,1)).total_seconds()

                snapshots_by_date = sorted([(timestamp(snapshot.committer_date),snapshot.sha) 
                                    for snapshot in snapshots_to_analyze],key = lambda x :x[0])
                diffs = [ {'group' : 'sequential', 
                           'key' : "%.6f" % snapshots_by_date[i][0], 
                           'snapshot_a': snapshots_by_date[i][1], 
                           'snapshot_b' :snapshots_by_date[i+1][1]} 
                           for i in range(len(snapshots_by_date)-1)]

                self.analyze_and_generate_diffs(branch,snapshots_to_analyze,diffs)

            except KeyboardInterrupt:
                raise

