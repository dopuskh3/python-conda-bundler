import os
import unittest
import shutil
import tempfile
from bundler import conda


class FakeCommand:
    def __init__(self, install_path):
        self.conda_url = conda.DEFAULT_CONDA_URL
        self.conda_install_path = install_path

    def announce(self, *args, **kwargs):
        pass


class CondaInstallTest(unittest.TestCase):

    def setUp(self):
        self._tmp_install_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmp_install_path)

    def test_install_conda_env(self):
        filename = conda.install_conda(FakeCommand(self._tmp_install_path))
        self.assertTrue(os.path.isfile(filename))
