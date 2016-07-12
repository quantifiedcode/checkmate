import os
import tempfile
import pytest
import subprocess

TEST_DIRECTORY = os.path.abspath(__file__+"/../")
DATA_DIRECTORY = os.path.join(TEST_DIRECTORY,"data")
GIT_TEST_REPOSITORY = DATA_DIRECTORY + "/test_repository/d3py.tar.gz"
