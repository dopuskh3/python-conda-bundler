#!/usr/bin/env python
"""Bundle package into a conda environment."""
import subprocess
from distutils.cmd import Command

import os
import re
import shutil
import tempfile
from distutils import log

from bundler import conda

BUNDLE_SUFFIX = "bundle"


class ShebangFixer:
    """Fix python script shebangs.

    Insert a bin/sh shebang on python file with a second line calling
    exec on python interpreter located in the same directory.
    """

    SHEBANG = "#!/bin/sh\n"
    MAGIC_PYTHON_EXEC_LINE = '"exec" "`dirname $0`/python" "$0" "$@"\n'

    def __init__(self, path):
        """Initialize.

        :param path: path of the script file to fix
        """
        self._path = path
        self._fixed = False

    def _should_fix(self):
        with open(self._path, 'r') as fd:
            try:
                first_line = fd.readline()
                if re.match('#!.+/python.*\n', first_line):
                    return True
            except UnicodeDecodeError:
                return False
        return False

    def fix(self):
        """Fix shebang if necessary."""
        if self._should_fix():
            with open(self._path, 'r') as fd:
                fd.readline()
                tmpfile = self._path + '.new'
                with open(tmpfile, 'w+') as target_fd:
                    target_fd.write(self.SHEBANG)
                    target_fd.write(self.MAGIC_PYTHON_EXEC_LINE)
                    target_fd.write(fd.read())
            os.rename(tmpfile, self._path)


class BundleCommand(Command):
    """Bundle setuptool command."""

    description = "Bundle application in a conda .tar.gz file"
    user_options = [
        # The format is (long option, short option, description).
        ('conda-packages=', None,
         'Coma-separated list of conda package specification to install in bundle'),
        ('conda-url=', None, 'URL to conda installer'),
        ('conda-bin=', None, 'Conda command to invoke'),
        ('conda-install-path=', None, 'Target path to install conda if conda-url is specified.'),
    ]

    def _get_output_build_name(self):
        return "{name}-{version}".format(
            name=self.distribution.metadata.get_name(),
            version=self.distribution.metadata.get_version()
        )

    @staticmethod
    def fix_env_shebang(env):
        """Fix python shebangs in env."""
        bin_path = os.path.join(env, 'bin')
        for binary in os.listdir(bin_path):
            binary_path = os.path.join(bin_path, binary)
            if not os.path.isfile(binary_path):
                continue
            ShebangFixer(binary_path).fix()

    def _get_conda_create_options(self):
        options = ['--yes', '--copy']
        # If there is no package to install, just clone current environment:
        if not self.conda_packages:
            options.extend(['--clone', self.conda_install_path])
        return options

    def get_conda_package_list(self):
        """Get list of conda package specifications to install."""
        if self.conda_packages:
            return self.conda_packages.split(',')
        return []

    def create_conda_env(self, path):
        """Create target conda environment."""
        command = ' '.join([self.conda_bin, 'create'] +
                           self._get_conda_create_options() +
                           ['--prefix', path] +
                           self.get_conda_package_list())

        self.announce("Running: %s" % command, level=log.INFO)
        subprocess.check_call(command, shell=True)

    def compress_bundle(self, path, archive_name):
        """Compress conda bundle."""
        compress_command = "tar -C {parent_dir} -zcf {archive_name} {path}".format(
            parent_dir=os.path.dirname(path),
            path=os.path.basename(path),
            archive_name=archive_name)
        self.announce("Running: %s" % compress_command, level=log.INFO)
        subprocess.check_call(compress_command, shell=True)

    def install_package(self, path, setup_file, *args):
        """Install current package by calling setup script install command."""
        python_path = os.path.join(path, "bin", "python")
        command = [python_path, setup_file, "install"] + list(args)
        self.announce("Running: %s" % command, level=log.INFO)
        subprocess.check_call(command)

    def initialize_options(self):
        """Initialize options."""
        self.conda_file = None
        self.conda_url = None
        self.conda_packages = None
        self.conda_install_path = tempfile.mkdtemp()
        self.conda_bin = 'conda'
        self.conda_env_build_path = os.path.join(tempfile.mkdtemp(), self._get_output_build_name())

    def finalize_options(self):
        """Finalize options."""
        if self.conda_file and not os.path.isfile(self.conda_file):
            raise IOError("%s do not exists." % self.conda_file)

    def run(self):
        """Run command."""
        tmp_archive_name = "{env_path}-{bundle_suffix}.tar.gz".format(
            bundle_suffix=BUNDLE_SUFFIX,
            env_path=self.conda_env_build_path)
        dist_directory = os.path.join(os.path.dirname(self.distribution.script_name),
                                      'dist')
        dist_file = os.path.join(dist_directory, os.path.basename(tmp_archive_name))
        if self.conda_url:
            self.conda_bin = conda.install_conda(self)

        self.create_conda_env(self.conda_env_build_path)
        self.fix_env_shebang(self.conda_env_build_path)
        self.install_package(self.conda_env_build_path, self.distribution.script_name)
        self.fix_env_shebang(self.conda_env_build_path)
        self.compress_bundle(self.conda_env_build_path, tmp_archive_name)

        if not os.path.isdir(dist_directory):
            os.makedirs(dist_directory)
        self.announce("Renaming %s -> %s" % (tmp_archive_name, dist_file), level=log.INFO)
        shutil.move(tmp_archive_name, dist_file)
