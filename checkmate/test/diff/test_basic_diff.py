from checkmate.lib.models import (Diff,
                                  DiffFileRevision,
                                  ProjectIssueClass,
                                  IssueClass,
                                  Issue,
                                  IssueOccurrence,
                                  FileRevision,
                                  Snapshot,
                                  DiffIssueOccurrence)

from checkmate.lib.code.environment import CodeEnvironment

from ..helpers import ProjectBasedTest

class TestDiffing(ProjectBasedTest):

    def test_simple_diff(self):
        snapshot_1 = Snapshot({'project' : self.project, 'hash' : 'snapshot_1'})
        file_revision_1 = FileRevision({'path' : 'foo.py','hash' : '1:foo.py', 'language' : 'python'})

        issue_class_1 = IssueClass({'code' : 'wildcard','analyzer' : 'example','severity' : 2})
        project_issue_class_1 = ProjectIssueClass({'project' : self.project,
                                                   'issue_class' : issue_class_1,
                                                   'enabled' : True})
        issue_1 = Issue({'code' : 'wildcard','analyzer' : 'example','fingerprint' : '1','project' : self.project})

        issue_1_occurrence = IssueOccurrence({'issue' : issue_1,
                                              'file_revision' : file_revision_1,
                                              'from_row' : 1,'from_column' : 0,
                                              'to_row' : 1,'to_column' : None})

        snapshot_1.file_revisions = [file_revision_1]

        with self.backend.transaction():
            self.backend.save(snapshot_1)
            self.backend.save(issue_class_1)
            self.backend.save(project_issue_class_1)
            self.backend.save(issue_1)
            self.backend.save(issue_1_occurrence)
            self.backend.commit()

        snapshot_2 = Snapshot({'project' : self.project, 'hash' : 'snapshot_2'})
        file_revision_2 = FileRevision({'path' : 'bar.py','hash' : '2:bar.py','language':'python'})
        snapshot_2.file_revisions = [file_revision_1,file_revision_2]
        issue_class_2 = IssueClass({'code' : 'format','analyzer' : 'example','severity' : 1})
        project_issue_class_2 = ProjectIssueClass({'project' : self.project,
                                                   'issue_class' : issue_class_2,
                                                   'enabled' : True})
        issue_2 = Issue({'code' : 'format','analyzer' : 'example','fingerprint' : '1','project' : self.project})
        issue_2_occurrence = IssueOccurrence({'issue' : issue_2,
                                              'file_revision' : file_revision_2,
                                              'from_row' : 2,'from_column' : 0,
                                              'to_row' : 3,'to_column' : None})

        with self.backend.transaction():
            self.backend.save(snapshot_2)
            self.backend.save(issue_class_2)
            self.backend.save(project_issue_class_2)
            self.backend.save(issue_2_occurrence)
            self.backend.save(issue_2)

        environment = CodeEnvironment(project = self.project,
                                      global_settings = self.settings,
                                      project_settings = {},
                                      file_revisions = [])

        #We make a simple diff
        diff,diff_file_revisions,diff_issue_occurrences = environment.diff_snapshots(snapshot_1,snapshot_2)

        #we expect one added file revision with 1 added issue occurrence
        assert len(diff_file_revisions) == 1
        assert len(diff_issue_occurrences) == 1
        assert diff_file_revisions[0].key == 'added'
        assert diff_file_revisions[0].file_revision == file_revision_2
        assert diff_issue_occurrences[0].key == 'added'
        assert diff_issue_occurrences[0].issue_occurrence == issue_2_occurrence

        snapshot_3 = Snapshot({'project' : self.project, 'hash' : 'snapshot_3'})
        file_revision_3 = FileRevision({'path' : 'bar.py','hash' : '3:bar.py','language' : 'python'})
        snapshot_3.file_revisions = [file_revision_1,file_revision_3]
        issue_2_occurrence_2 = IssueOccurrence({'issue' : issue_2,
                                              'file_revision' : file_revision_3,
                                              'from_row' : 2,'from_column' : 0,
                                              'to_row' : 3,'to_column' : None})
        issue_2_occurrence_3 = IssueOccurrence({'issue' : issue_2,
                                                'file_revision' : file_revision_3,
                                                'from_row' : 3,'from_column' :4,
                                                'to_row' : 5,'to_column' : 8})

        self.backend.save(issue_2_occurrence_2)
        self.backend.save(issue_2_occurrence_3)
        self.backend.save(snapshot_3)

        #We make a simple diff of the next snapshot
        diff,diff_file_revisions,diff_issue_occurrences = environment.diff_snapshots(snapshot_2,snapshot_3)

        #again, we expect one file revision and one issue occurrence associated with the diff
        assert len(diff_file_revisions) == 1
        assert len(diff_issue_occurrences) == 1

        assert diff_file_revisions[0].key == 'modified'
        assert diff_issue_occurrences[0].key == 'added'

        issues_count_by_severity = diff.get_issues_count(by_severity=True)

        assert issues_count_by_severity['added'][1] == 1
        assert issues_count_by_severity['fixed'] == {}

        issues_count = diff.get_issues_count()

        assert issues_count['added'] == 1
        assert issues_count['fixed'] == 0

        summarized_issues = diff.summarize_issues()

        assert 'added' in summarized_issues
        assert '' in summarized_issues['added']
        assert 'python' in summarized_issues['added']['']
        assert 'example' in summarized_issues['added']['']['python']
        assert 'format' in summarized_issues['added']['']['python']['example']
        assert summarized_issues['added']['']['python']['example']['format'] == [1,1] 
        assert 'fixed' in summarized_issues and not summarized_issues['fixed']
