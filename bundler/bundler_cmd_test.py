import os
import shutil
import sys
import tempfile
import unittest

import setuptools

from bundler import bundler_cmd, conda

SAMPLE_FILE = """#!/boo/bar/python

bar"""


class ShebangFixerTest(unittest.TestCase):
    def setUp(self):
        self._script = tempfile.mktemp()

    def tearDown(self):
        if os.path.isfile(self._script):
            os.remove(self._script)

    def test_fix_shebang(self):
        with open(self._script, 'w+') as fd:
            fd.write(SAMPLE_FILE)
        fixer = bundler_cmd.ShebangFixer(self._script)
        fixer.fix()
        with open(self._script, 'r') as new_file_fd:
            self.assertEquals(new_file_fd.readline(),
                              bundler_cmd.ShebangFixer.SHEBANG)
            self.assertEquals(new_file_fd.readline(),
                              bundler_cmd.ShebangFixer.MAGIC_PYTHON_EXEC_LINE)

    def test_fix_shebang_detect_bin_files(self):
        self.assertFalse(bundler_cmd.ShebangFixer(sys.executable)._should_fix())


class BundlerCommandTest(unittest.TestCase):
    def _get_distribution(self):
        dist = setuptools.Distribution()
        dist.script_name = self._fake_setup_script
        return dist

    def _create_fake_setup_script(self, python_executable):
        with open(self._fake_setup_script, 'w') as fd:
            fd.write("""#!/usr/bin/env python
import sys
print(sys.executable)
assert(sys.executable == \"{expected_executable}\")
if sys.argv[1] != 'install':
    raise RuntimeError('Invalid first argument')
""".format(expected_executable=python_executable))

    def setUp(self):
        self._env_build_path = tempfile.mkdtemp()
        self._fake_setup_script = tempfile.mktemp()

    def tearDown(self):
        if os.path.isdir(self._env_build_path):
            shutil.rmtree(self._env_build_path)
        os.remove(self._fake_setup_script)

    def test_create_conda_env(self):
        command = bundler_cmd.BundleCommand(self._get_distribution())
        command.initialize_options()
        command.conda_url = conda.DEFAULT_CONDA_URL
        command.bundle_build_dir = self._env_build_path
        command.finalize_options()
        self._create_fake_setup_script(os.path.join(command.bundle_build_path, 'bin', 'python'))
        command.distribution.script_name = self._fake_setup_script
        command.run()
