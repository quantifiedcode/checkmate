from ...lib.repository import Repository
from ..helpers import RepositoryBasedTest

import tempfile
import os
import shutil

class TestRepository(RepositoryBasedTest):

    gzip_filename = "test_repository/d3py.tar.gz"

    def setUp(self):
        super(TestRepository,self).setUp()
        self.repository = Repository(path = self.tmp_project_path)
        self.tmpdir_blank_repo = tempfile.mkdtemp()
        self.blank_repository = Repository(path = self.tmpdir_blank_repo)

    def tearDown(self):
        shutil.rmtree(self.tmpdir_blank_repo)
        super(TestRepository,self).tearDown()

    def test_init(self):

        self.blank_repository.init()
        assert os.path.exists(self.blank_repository.path+"/.git")
        assert os.path.isdir(self.blank_repository.path+"/.git")

    def test_add_remote(self):

        self.blank_repository.init()
        self.blank_repository.add_remote(url = self.tmp_project_path,name = "my_origin")
        self.blank_repository.get_remotes()
        assert self.blank_repository.get_remotes() == [{'name' : 'my_origin','url' : self.tmp_project_path}]

    def test_pull_master_from_origin(self):

        self.blank_repository.init()
        self.blank_repository.add_remote(url = self.tmp_project_path,name = "my_origin")
        self.blank_repository.pull("my_origin","master")
        set(os.listdir(self.blank_repository.path))
        assert set(['README.md','d3py','setup.py','tests'])\
               .issubset(set(os.listdir(self.blank_repository.path)))

    def test_get_files_in_commit(self):

        commit_sha = 'e29a09687b91381bf96034fcf1921956177c2d54'
        files_in_commit = self.repository.get_files_in_commit(commit_sha)
        valid_files_in_commit = set([u'd3py/geoms/bar.py',
                                     u'd3py/templates.py',
                                     u'd3py/geoms/area.py',
                                     u'examples/d3py_line.py',
                                     u'd3py/geoms/geom.py',
                                     u'd3py/__init__.py',
                                     u'examples/d3py_area.py',
                                     u'tests/test_javascript.py',
                                     u'examples/d3py_scatter.py',
                                     u'd3py/geoms/__init__.py',
                                     u'examples/d3py_bar.py',
                                     u'd3py/geoms/xaxis.py',
                                     u'.gitignore',
                                     u'd3py/d3.js',
                                     u'examples/d3py_vega_scatter.py',
                                     u'd3py/networkx_figure.py',
                                     u'README.md',
                                     u'examples/d3py_multiline.py',
                                     u'examples/d3py_vega_line.py',
                                     u'setup.py',
                                     u'd3py/javascript.py',
                                     u'd3py/css.py',
                                     u'd3py/geoms/yaxis.py',
                                     u'tests/test_figure.py',
                                     u'd3py/geoms/line.py',
                                     u'd3py/vega.py',
                                     u'd3py/d3py_template.html',
                                     u'd3py/pandas_figure.py',
                                     u'examples/d3py_graph.py',
                                     u'd3py/geoms/Readme.md',
                                     u'examples/d3py_vega_area.py',
                                     u'examples/d3py_vega_bar.py',
                                     u'd3py/geoms/point.py',
                                     u'd3py/HTTPHandler.py',
                                     u'd3py/test.py',
                                     u'd3py/vega_template.html',
                                     u'd3py/figure.py',
                                     u'd3py/geoms/graph.py'])
        assert set([f['path'] for f in files_in_commit]) == valid_files_in_commit
