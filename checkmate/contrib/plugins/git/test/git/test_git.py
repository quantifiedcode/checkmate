from ...lib.repository import Repository
from ..helpers import RepositoryBasedTest

import tempfile
import os
import shutil

class TestRepository(RepositoryBasedTest):

    gzip_filename = "test_repository/d3py.tar.gz"

    def test_snapshots(self):
        snapshots = self.project.git.get_snapshots(branch = "origin/master")

        assert len(snapshots) == 157

        assert snapshots[0].project == self.project

    def test_file_revisions(self):
        snapshot = self.project.git.get_snapshots(branch = "origin/master")[-1]
        file_revisions = self.project.git.get_file_revisions(snapshot['sha'])
        assert len(file_revisions) == 38
        assert 'd3py/HTTPHandler.py' in [f.path for f in file_revisions]
