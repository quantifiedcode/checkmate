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
from checkmate.lib.git.repository import Repository
import checkmate.tests.settings as settings
import tempfile
import os
import os.path
import subprocess
import datetime

@pytest.fixture(scope = "module")
def test_repository_directory(request):

    tmpdir = tempfile.mkdtemp()
    subprocess.call(["tar","-xzf",settings.GIT_TEST_REPOSITORY],cwd = tmpdir)

    def finalizer():
        subprocess.call(["rm","-rf",tmpdir])

    request.addfinalizer(finalizer)

    return tmpdir

@pytest.fixture(scope = "function")
def tmpdir(request):

    tmpdir = tempfile.mkdtemp()
    def finalizer():
        subprocess.call(["rm","-rf",tmpdir])
    request.addfinalizer(finalizer)
    return tmpdir

@pytest.fixture(scope = "function")
def blank_repository(request,tmpdir):

    repository = Repository(path = tmpdir)
    return repository

@pytest.fixture(scope = "function")
def initialized_repository(request,blank_repository,test_repository_directory):

    blank_repository.init()
    blank_repository.add_remote(url = test_repository_directory,name = "my_origin")
    blank_repository.pull(remote = "my_origin",branch = "master")
    return blank_repository

def test_init(blank_repository):

    blank_repository.init()
    assert os.path.exists(blank_repository.path+"/.git")
    assert os.path.isdir(blank_repository.path+"/.git")

def test_add_remote(blank_repository,test_repository_directory):

    blank_repository.init()
    blank_repository.add_remote(url = test_repository_directory,name = "my_origin")
    assert blank_repository.get_remotes() == ["my_origin"]

def test_pull_master_from_origin(initialized_repository):

    initialized_repository.pull("master","my_origin")
    assert set(['README.md','d3py','setup.py','tests']).issubset(set(os.listdir(initialized_repository.path)))

def test_get_files_in_commit(initialized_repository):
    
    commit_sha = 'e29a09687b91381bf96034fcf1921956177c2d54'
    files_in_commit = initialized_repository.get_files_in_commit(commit_sha)
    valid_files_in_commit = ['README.md', 'd3py/HTTPHandler.py', 'd3py/__init__.py', 'd3py/css.py', 'd3py/d3.js', 'd3py/d3py_template.html', 'd3py/figure.py', 'd3py/geoms/Readme.md', 'd3py/geoms/__init__.py', 'd3py/geoms/area.py', 'd3py/geoms/bar.py', 'd3py/geoms/geom.py', 'd3py/geoms/graph.py', 'd3py/geoms/line.py', 'd3py/geoms/point.py', 'd3py/geoms/xaxis.py', 'd3py/geoms/yaxis.py', 'd3py/javascript.py', 'd3py/networkx_figure.py', 'd3py/pandas_figure.py', 'd3py/templates.py', 'd3py/test.py', 'd3py/vega.py', 'd3py/vega_template.html', 'examples/d3py_area.py', 'examples/d3py_bar.py', 'examples/d3py_graph.py', 'examples/d3py_line.py', 'examples/d3py_multiline.py', 'examples/d3py_scatter.py', 'examples/d3py_vega_area.py', 'examples/d3py_vega_bar.py', 'examples/d3py_vega_line.py', 'examples/d3py_vega_scatter.py', 'setup.py', 'tests/test_figure.py', 'tests/test_javascript.py']
    assert files_in_commit == valid_files_in_commit