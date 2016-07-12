
from checkmate.contrib.plugins.git.commands.analyze import Command as AnalyzeCommand
from checkmate.contrib.plugins.git.models import GitSnapshot
from checkmate.lib.models import (Diff,
                                  DiffFileRevision,
                                  DiffIssueOccurrence)

from ..helpers import RepositoryBasedTest

class TestProjectDiffing(RepositoryBasedTest):

    gzip_filename = "diff_project.tar.gz"

    """
    Change history in repository:

    * We added a file                  - a.py
    * We add a file                    - b.py
    * We modify a file                 - a.py
    """

    file_revision_history = [
        {
            'added'  : 1
        },
        {
            'added' : 1,
        },
        {
            'modified' : 1
        },
    ]
    def test_number_of_snapshots(self):

        #how to handle project-specific settings?
        analyze_command = AnalyzeCommand(self.project,
                                         self.settings,
                                         self.backend)
        analyze_command.opts['n'] = 3
        analyze_command.opts['branch'] = 'master'
        analyze_command.run()

        repository = self.project.git.repository
        git_snapshots = self.project.git.get_snapshots(branch = 'master')[::-1]
        snapshots = self.backend.filter(GitSnapshot,{}).sort('committer_date',-1)

        assert len(snapshots) == 3

        for snapshot,git_snapshot in zip(snapshots,git_snapshots[:len(snapshots)]):
            assert snapshot['sha'] == git_snapshot['sha']

    def test_presence_of_diffs(self):

        #how to handle project-specific settings?
        analyze_command = AnalyzeCommand(self.project,
                                         self.settings,
                                         self.backend)
        analyze_command.opts['n'] = 3
        analyze_command.opts['branch'] = 'master'
        analyze_command.run()

        snapshots = self.backend.filter(GitSnapshot,{}).sort('committer_date',1)

        assert len(self.backend.filter(Diff,{})) == 2

        assert len(self.backend.filter(Diff,{})) == 2

        assert len(self.backend.filter(DiffFileRevision,{})) == 2
        assert len(self.backend.filter(DiffIssueOccurrence,{})) == 2

        i = 0
        for last_snapshot,snapshot in zip(snapshots[:-1],snapshots[1:]):
            diff = self.backend.get(Diff,{'snapshot_a.git_snapshot' : last_snapshot,
                                          'snapshot_b.git_snapshot' : snapshot})
            assert diff.issue_occurrences
            print len(diff.issue_occurrences) == 10
            if i == 0:
                assert len(diff.file_revisions) == 1
                assert len(diff.file_revisions.filter({'key' : 'deleted'})) == 1
            i+=1
