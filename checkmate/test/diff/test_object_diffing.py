from unittest import TestCase

from checkmate.lib.models import (Diff,
                                  DiffFileRevision,
                                  Issue,
                                  IssueOccurrence,
                                  FileRevision,
                                  Snapshot,
                                  DiffIssueOccurrence)

from checkmate.lib.code.environment import (diff_objects,
                                            file_revision_key,
                                            file_revision_comparator,
                                            issue_occurrence_key,
                                            issue_occurrence_comparator)

class TestObjectDiffing(TestCase):

    def test_issue_occurrence_diffing(self):

        file_revision = FileRevision({'path' : 'foo.py'})
        issue_1 = Issue({'analyzer' : 'test','code' : 'test1','fingerprint' : 'foo'})
        issue_2 = Issue({'analyzer' : 'test','code' : 'test2','fingerprint' : 'bar'})

        issue_occurrence_1 = IssueOccurrence({'issue' : issue_1,
                                              'file_revision' : file_revision,
                                              'from_row' : 1,
                                              'from_column' : 0,
                                              'to_row' : 1,
                                              'to_column': None})
        issue_occurrence_2 = IssueOccurrence({'issue' : issue_1,
                                              'file_revision' : file_revision,
                                              'from_row' : 1,
                                              'from_column' : 0,
                                              'to_row' : 1,
                                              'to_column' : None})
        issue_occurrence_3 = IssueOccurrence({'issue' : issue_2,
                                              'file_revision' : file_revision,
                                              'from_row' : 2,
                                              'from_column' : 0,
                                              'to_row' : 3,
                                              'to_column' : 10})
        issue_occurrence_4 = IssueOccurrence({'issue' : issue_1,
                                              'file_revision' : file_revision,
                                              'from_row' : 10,
                                              'from_column' : 0,
                                              'to_row' : 20,
                                              'to_column' : None})

        assert issue_occurrence_key(issue_occurrence_1) == issue_occurrence_key(issue_occurrence_2)
        assert issue_occurrence_key(issue_occurrence_3) != issue_occurrence_key(issue_occurrence_1)
        assert issue_occurrence_comparator(issue_occurrence_1,issue_occurrence_2) == 0
        assert issue_occurrence_comparator(issue_occurrence_1,issue_occurrence_4) == -1
        assert issue_occurrence_comparator(issue_occurrence_1,issue_occurrence_3) == -1

        result = diff_objects([issue_occurrence_1,issue_occurrence_3],
                              [issue_occurrence_1,issue_occurrence_2,issue_occurrence_4],
                              key = issue_occurrence_key,
                              comparator = issue_occurrence_comparator)

        for key,issue_occurrences in result.items():
            if key == 'added':
                assert len(issue_occurrences) == 2
                assert issue_occurrence_4 in issue_occurrences
                assert issue_occurrence_2 in issue_occurrences
            elif key == 'modified':
                assert len(issue_occurrences) == 0
            elif key == 'deleted':
                assert len(issue_occurrences) == 1
                assert issue_occurrence_3 in issue_occurrences

        result = diff_objects([issue_occurrence_1],
                              [issue_occurrence_1,issue_occurrence_2,issue_occurrence_3],
                              key = issue_occurrence_key,
                              comparator = issue_occurrence_comparator)

        for key,issue_occurrences in result.items():
            if key == 'added':
                assert len(issue_occurrences) == 2
                assert issue_occurrence_3 in issue_occurrences
                assert issue_occurrence_1 in issue_occurrences or issue_occurrence_2 in issue_occurrences
            elif key == 'modified':
                assert len(issue_occurrences) == 0
            elif key == 'deleted':
                assert len(issue_occurrences) == 0

        result = diff_objects([issue_occurrence_1,issue_occurrence_2,issue_occurrence_3],
                              [issue_occurrence_3],
                              key = issue_occurrence_key,
                              comparator = issue_occurrence_comparator)

        for key,issue_occurrences in result.items():
            if key == 'added':
                assert len(issue_occurrences) == 0
            elif key == 'modified':
                assert len(issue_occurrences) == 0
            elif key == 'deleted':
                assert len(issue_occurrences) == 2
                assert issue_occurrence_1 in issue_occurrences
                assert issue_occurrence_2 in issue_occurrences

    def test_file_revision_diffing(self):

        file_revision_1 = FileRevision({'path' : 'foo.py','hash' : 'foo.py:1'})
        file_revision_2 = FileRevision({'path' : 'foo.py','hash' : 'foo.py:2'})
        file_revision_3 = FileRevision({'path' : 'bar.py','hash' : 'bar.py:1'})
        file_revision_4 = FileRevision({'path' : 'bar.py','hash' : 'bar.py:2'})

        assert file_revision_key(file_revision_1) == file_revision_key(file_revision_2)
        assert file_revision_key(file_revision_1) != file_revision_key(file_revision_3)
        assert file_revision_comparator(file_revision_1,file_revision_2) == -1

        result = diff_objects([file_revision_1],
                              [file_revision_2],
                              key = file_revision_key,
                              comparator = file_revision_comparator)

        for key,file_revisions in result.items():
            if key == 'added':
                assert len(file_revisions) == 0
            elif key == 'modified':
                assert len(file_revisions) == 1
            elif key == 'deleted':
                assert len(file_revisions) == 0

        result = diff_objects([file_revision_1],
                              [file_revision_2,file_revision_3],
                              key = file_revision_key,
                              comparator = file_revision_comparator)

        for key,file_revisions in result.items():
            if key == 'added':
                assert len(file_revisions) == 1
                assert file_revision_3 in file_revisions
            elif key == 'modified':
                assert len(file_revisions) == 1
                assert file_revision_1 in file_revisions
                assert file_revision_2 not in file_revisions
            elif key == 'deleted':
                assert len(file_revisions) == 0

        result = diff_objects([file_revision_1,file_revision_3],
                              [file_revision_2],
                              key = file_revision_key,
                              comparator = file_revision_comparator)

        for key,file_revisions in result.items():
            if key == 'added':
                assert len(file_revisions) == 0
            elif key == 'modified':
                assert len(file_revisions) == 1
                assert file_revision_1 in file_revisions
                assert file_revision_2 not in file_revisions
            elif key == 'deleted':
                assert len(file_revisions) == 1
                assert file_revision_3 in file_revisions
