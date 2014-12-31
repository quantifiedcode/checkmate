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

import pytest

from checkmate.lib.models import Project
import checkmate.tests.settings as settings

from checkmate.tests.lib.git.test_repository import test_repository_directory

@pytest.fixture(scope = "function")
def project(request,test_repository_directory):
    return Project({'path' : test_repository_directory})

def test_snapshots(project):
    snapshots = project.get_git_snapshots(branch = "master")

    assert len(snapshots) == 157

    assert snapshots[0].project == project

def test_file_revisions(project):
    snapshot = project.get_git_snapshots()[0]
    file_revisions = snapshot.get_file_revisions()
    assert len(file_revisions) == 37
    assert 'd3py/HTTPHandler.py' in [f.path for f in file_revisions]

    assert file_revisions[0].snapshot == snapshot