from . import RepositoryBasedTest

from checkmate.contrib.plugins.git.commands.analyze import Command as AnalyzeCommand
from checkmate.contrib.plugins.git.models import GitSnapshot, GitBranch
from checkmate.lib.models import Issue, IssueOccurrence
from checkmate.lib.analysis import BaseAnalyzer

class TestProjectAnalysis(RepositoryBasedTest):

    def test_analyze(self):
        #how to handle project-specific settings?
        analyze_command = AnalyzeCommand(self.project,
                                         self.settings,
                                         self.backend)
        analyze_command.opts['n'] = 1
        analyze_command.opts['branch'] = 'origin/master'
        analyze_command.run()

        snapshot = self.backend.get(GitSnapshot,{})
        assert snapshot
        issues = self.backend.filter(Issue,{})
        assert len(issues) == 1
        issue_occurrences = self.backend.filter(IssueOccurrence,{})
        assert len(issue_occurrences) == 3
        branch = self.backend.get(GitBranch,{})
        assert branch.name == 'origin/master'
