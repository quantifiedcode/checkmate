# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from checkmate.management.commands.analyze import Command as AnalyzeCommand
from .base import Command as BaseCommand
from ..lib.repository import group_snapshots_by_date,get_first_date_for_group
from ..models import GitBranch,GitSnapshot
from ..helpers import Git
from checkmate.lib.models import Diff, Snapshot
from checkmate.helpers.hashing import Hasher
from checkmate.helpers.settings import update

import time
import datetime
import traceback
import logging

from checkmate.lib.code import CodeEnvironment

logger = logging.getLogger(__name__)

class Command(BaseCommand,AnalyzeCommand):

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
        'default'     : 'master',
        'help'        : 'The branch to analyze.'
        },
        {
        'name'        : '--from',
        'action'      : 'store',
        'dest'        : 'from',
        'type'        : str,
        'default'     : '',
        'help'        : 'The date for which to perform the analysis.'
        },
        {
        'name'        : '--type',
        'action'      : 'store',
        'dest'        : 'type',
        'type'        : str,
        'default'     : 'latest',
        'help'        : 'The type of analysis (latest, monthly, weekly, daily).'
        },
        ]

    def analyze_grouped_snapshots(self,branch,group,grouped_snapshots):
        for key,snapshots in grouped_snapshots.items():
            last_snp,first_snp = snapshots[0],snapshots[-1]
            self.analyze_and_generate_diffs(branch,
                                            [first_snp,last_snp],
                                            [{'snapshot_a' : first_snp.sha,
                                              'snapshot_b' : last_snp.sha}])

    def analyze_and_generate_diffs(self,branch,snapshots,diff_list):

        analyzed_snapshots = {}
        new_analyzed_snapshots = {}

        if 'project_settings' in self.opts:
            project_settings = self.opts['project_settings']
        else:
            project_settings = self.project.settings

        #we look for a .checkmate.yml file in the main branch of the project
        #if we find it, we either replace the project settings, update them
        #or do nothing, depending on the desired configuration.
        try:
            git_settings = self.project.git.get_settings()
            if git_settings is not None:
                if git_settings.get('overwrite_project_settings',False):
                    project_settings = git_settings
                elif not project_settings.get('ignore_git_settings',False):
                    project_settings.update(git_settings)
        except ValueError:
            logger.warning("Error when loading checkmate settings from git...")
            git_settings = {}

        code_environment = CodeEnvironment(self.project,
                                           global_settings=self.settings,
                                           project_settings=project_settings)

        code_environment.env['branch'] = branch
        code_environment.env['project'] = self.project

        for git_snapshot in snapshots:
            try:
                query = {'sha' : git_snapshot.sha,
                         'project' : self.project}
                git_snapshot = self.backend.get(GitSnapshot,query,include = ('snapshot',))
                snapshot = git_snapshot.snapshot
                #we check if the snapshot is analyzed and if the analysis configuration matches
                if snapshot.analyzed and snapshot.configuration == self.project.configuration:
                    analyze_snapshot = False
                else:
                    analyze_snapshot = True
                    snapshot.configuration = self.project.configuration
            except GitSnapshot.DoesNotExist:
                analyze_snapshot = True
                snapshot = Snapshot()
                snapshot.configuration = self.project.configuration
            except GitSnapshot.MultipleDocumentsReturned:
                logger.error("Multiple snapshots returned, deleting...")
                with self.backend.transaction():
                    self.backend.filter(GitSnapshot,query).delete()
                analyze_snapshot = True

            if analyze_snapshot:

                try:
                    file_revisions = self.project.git.get_file_revisions(git_snapshot.sha)
                except:
                    logger.error("Cannot fetch file revisions for snapshot %s in project %s" % (git_snapshot.sha,self.project.pk) )
                    continue

                code_environment.file_revisions = file_revisions
                git_snapshot.snapshot = code_environment.analyze(file_revisions, save_if_empty = True, snapshot=snapshot)

                new_analyzed_snapshots[git_snapshot.sha] = git_snapshot

                with self.backend.transaction():
                    git_snapshot.snapshot.hash = git_snapshot.sha
                    self.backend.save(git_snapshot.snapshot)
                    git_snapshot.project = self.project
                    self.backend.save(git_snapshot)

            analyzed_snapshots[git_snapshot.sha] = git_snapshot

        snapshot_pairs = []
        for diff_params in diff_list:
            try:
                snapshot_pairs.append([analyzed_snapshots[diff_params['snapshot_a']]
                                      ,analyzed_snapshots[diff_params['snapshot_b']]])
            except KeyError:
                continue

        diffs = []

        for git_snapshot_a,git_snapshot_b in snapshot_pairs:
            diff = None
            try:
                query = {'snapshot_a' : git_snapshot_a.snapshot,
                         'snapshot_b' : git_snapshot_b.snapshot}
                diff = self.backend.get(Diff,query)
            except Diff.DoesNotExist:
                logger.info("Generating a diff between snapshots %s and %s" % (git_snapshot_a.sha,
                                                                               git_snapshot_b.sha))
            #if the configuration of the diff does not match the project configuration, we regenerate it
            if diff is None or diff.configuration != self.project.configuration:
                if diff is not None:
                    diff.configuration = self.project.configuration
                diff,diff_file_revisions,diff_issue_occurrences = code_environment.diff_snapshots(
                                                            git_snapshot_a.snapshot,
                                                            git_snapshot_b.snapshot,
                                                            save = True,
                                                            diff = diff)

            diffs.append(diff)

        return analyzed_snapshots,diffs

    def update_branch(self,branch_name,head_snapshot = None):

        logger.info("Updating info for branch %s" % branch_name)

        hasher = Hasher()
        hasher.add(branch_name)

        branch = GitBranch({'project' : self.project,
                            'name' : branch_name,
                            'hash' : hasher.digest.hexdigest(),
                            'snapshots' : [] })

        try:
            branch = self.backend.get(GitBranch,
                                      {'project.pk' : self.project.pk,'name' : branch_name})
        except GitBranch.DoesNotExist:
            logger.info("Creating branch....")
            #we save the new branch instead...
            with self.backend.transaction():
                self.backend.save(branch)

        if head_snapshot:
            if branch.get('head_snapshot'):
                if head_snapshot.committer_date_ts > branch.head_snapshot.eager.committer_date_ts:
                    branch.last_analyzed_snapshot    = branch.head_snapshot
                    branch.head_snapshot = head_snapshot
            else:
                branch.head_snapshot = head_snapshot
            with self.backend.transaction():
                self.backend.update(branch,['last_analyzed_snapshot','head_snapshot'])

    def run(self):
        #to do: replace this with actual configuration information (in the future)
        hasher = Hasher()
        hasher.add("bars")
        self.project.configuration = hasher.digest.hexdigest()
        with self.backend.transaction():
            self.backend.update(self.project,['configuration'])
        if not 'branch' in self.opts:
            branch_name = self.project.git.get_default_branch()
        else:
            branch_name = self.opts.get('branch')

        if self.opts['type'] in ('monthly','weekly','daily'):

            if not branch_name:
                raise ValueError("Branch cannot be None for %s analysis!" % self.opts['type'])

            logger.info("Analyzing %d %s commits in branch %s (offset: %d)" %
                (self.opts['n'],self.opts['type'],branch_name,self.opts['offset']))

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
                    logger.info("No snapshots found in branch %s" % branch_name)
                    return

            dt = get_first_date_for_group(from_date,self.opts['type'],self.opts['n']+\
                 self.opts['offset'])

            snapshots = self.project.git.get_snapshots(branch = branch_name,
                                                       since = dt.ctime())[:-self.opts['offset']
                                                       if self.opts['offset'] != 0 else None]

            grouped_snapshots = group_snapshots_by_date(snapshots,self.opts['type'])

            snapshots_to_analyze = []
            diffs_to_generate = []
            for key,snapshots in grouped_snapshots.items():
                last_snp,first_snp = snapshots[0],snapshots[-1]
                snapshots_to_analyze.append(first_snp)
                snapshots_to_analyze.append(last_snp)
                diffs_to_generate.append({'snapshot_a' : first_snp.sha, 'snapshot_b' : last_snp.sha})

        else:
            if self.opts['shas']:
                logger.info("Analyzing %d snapshots" % len(self.opts['shas'].split(",")))
                if isinstance(self.opts['shas'],(str,unicode)):
                    shas = self.opts['shas'].split(",")
                else:
                    shas = self.opts['shas']
                snapshots_to_analyze = self.project.git.get_snapshots(shas = shas)
            else:
                if branch_name is None:
                    logger.error("No branch specified!")
                    return

                #we perform a sequential analysis
                branch = None
                try:
                    branch = self.backend.get(GitBranch,
                                              {'project.pk' : self.project.pk,
                                               'name' : branch_name})
                except GitBranch.DoesNotExist:
                    pass

                logger.info("Analyzing the %d most recent commits in branch %s (offset: %d)" %
                    (self.opts['n'],branch_name,self.opts['offset']))

                if not self.opts['n']:
                    snapshots_to_analyze = self.project.git.get_snapshots(branch = branch_name)
                else:
                    snapshots_to_analyze = self.project.git.get_snapshots(branch = branch_name,
                        limit = self.opts['n'],offset = self.opts['offset'])

                def timestamp(dt):
                    return (dt-datetime.datetime(1970,1,1)).total_seconds()

                diffs_to_generate = [{'snapshot_a': snapshots_to_analyze[i]['sha'],
                                      'snapshot_b' :snapshots_to_analyze[i+1]['sha']}
                                      for i in range(len(snapshots_to_analyze)-1)]

                if branch and branch.get('last_analyzed_snapshot',None):
                    last_analyzed_snapshot = branch.last_analyzed_snapshot.eager
                    if last_analyzed_snapshot and snapshots_to_analyze and last_analyzed_snapshot['sha'] != snapshots_to_analyze[-1]['sha']:
                        snapshots_to_analyze.append(last_analyzed_snapshot)
                        last_diff = {
                                'snapshot_a' : last_analyzed_snapshot['sha'],
                                'snapshot_b' : snapshots_to_analyze[-1]['sha']
                            }
                        diffs_to_generate.append(last_diff)

            if 'diffs' in self.opts and self.opts['diffs'] is not None:
                diffs_to_generate = self.opts['diffs']

            try:
                analyzed_snapshots,diffs = self.analyze_and_generate_diffs(branch_name,
                                                                     snapshots_to_analyze
                                                                     ,diffs_to_generate)
                head_snapshot = None
                if analyzed_snapshots:
                    head_snapshot = sorted(analyzed_snapshots.values(),key = lambda snp : snp['committer_date_ts'])[-1]
                    if branch_name:
                        self.update_branch(branch_name,head_snapshot = head_snapshot)
            except KeyboardInterrupt:
                raise
