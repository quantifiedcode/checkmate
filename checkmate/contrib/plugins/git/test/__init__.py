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

import os
import tempfile
import pytest
import subprocess

TEST_DIRECTORY = os.path.abspath(__file__+"/../")

DATA_DIRECTORY = os.path.join(TEST_DIRECTORY,"data")

GIT_TEST_REPOSITORY = DATA_DIRECTORY + "/test_repository/d3py.tar.gz"

@pytest.fixture(scope = "module")
def test_repository_directory(request):

    tmpdir = tempfile.mkdtemp()
    print GIT_TEST_REPOSITORY
    subprocess.call(["tar","-xzf",GIT_TEST_REPOSITORY],cwd = tmpdir)

    def finalizer():
        subprocess.call(["rm","-rf",tmpdir])

    request.addfinalizer(finalizer)

    return tmpdir
