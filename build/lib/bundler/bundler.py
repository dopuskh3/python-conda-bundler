#!/usr/bin/env python
import subprocess
import sys
from distutils.cmd import Command

import os
import re
import shutil
import tempfile

from bundler import conda

BUNDLE_SUFFIX = "bundle"


def pmoab_dep_url(package_path):
    return "git+http://review.criteois.lan/%s" % package_path



class BundleCommand(Command):

    description = "Bundle application in a conda .tar.gz file"
    user_options = [
        # The format is (long option, short option, description).
        ('conda-file=', None, 'Path to a file containing conda env specs'),
        ('conda-url=', None, 'URL to conda installer')
    ]

    def __init__(self, dist):
        super().__init__(dist)

    def _get_output_build_name(self):
        return "{name}-{version}".format(
            name=self.distribution.metadata.get_name(),
            version=self.distribution.metadata.get_version()
        )

    def fix_env_shebang(env):
        bin_path = os.path.join(env, 'bin')
        for binary in os.listdir(bin_path):
            binary_path = os.path.join(bin_path, binary)
            if not os.path.isfile(binary_path):
                continue

            with open(binary_path, 'r') as fdesc:
                try:
                    firstline = fdesc.readline()
                    if re.match('#!.+bin/python.*', firstline):
                        fix_file(binary_path, fdesc)
                        print("Fixing %s" % binary_path)
                except UnicodeDecodeError:
                    continue

    def create_conda_env(path):
        command = ' '.join(['conda', 'create', '--yes', '--copy', '--prefix', path, 'python'])
        print("Running: %s" % command)
        p = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr, shell=True)
        p.communicate()
        p.wait()
        if p.returncode != 0:
            raise RuntimeError("Failed to create conda env in %s" % path)

    def compress_bundle(path, archive_name):
        compress_command = "tar -C {parent_dir} -zcf {archive_name} {path}".format(
            parent_dir=os.path.dirname(path),
            path=os.path.basename(path),
            archive_name=archive_name)
        print("Running: %s" % compress_command)
        subprocess.check_call(compress_command, shell=True)

    def install_package(path, setup_file, *args):
        python_path = os.path.join(path, "bin", "python")
        command = [python_path, setup_file, "install"] + list(args)
        print("Running: %s" % command)
        subprocess.check_call(command)

    def fix_file(path, sdesc):
        tmpfile = path + '.new'
        os.rename(path, tmpfile)
        with open(tmpfile, 'w+') as tdesc:
            tdesc.write('# !/bin/sh\n')
            tdesc.write('"exec" "`dirname $0`/python" "$0" "$@"\n')
            tdesc.write(sdesc.read())
        sdesc.close()
        os.rename(tmpfile, path)

    def initialize_options(self):
        self.conda_file = None
        self.conda_url = None

    def finalize_options(self):
        if not os.path.isfile(self.conda_file):
            raise IOError("%s do not exists." % self.conda_file)

    def run(self):
        build_dir = tempfile.mkdtemp()
        env_path = os.path.join(build_dir, self._get_output_build_name())
        tmp_archive_name = "{env_path}-{bundle_suffix}.tar.gz".format(
            bundle_suffix=BUNDLE_SUFFIX,
            env_path=env_path)
        dist_directory = os.path.join(os.path.dirname(self.distribution.script_name),
                                      'dist')
        dist_file = os.path.join(dist_directory, os.path.basename(tmp_archive_name))
        if self.conda_url:
            conda.install_conda(self.conda_url)

        self.create_conda_env(env_path)
        self.fix_env_shebang(env_path)
        self.install_package(env_path, self.distribution.script_name)
        self.fix_env_shebang(env_path)
        self.compress_bundle(env_path, tmp_archive_name)

        if not os.path.isdir(dist_directory):
            os.makedirs(dist_directory)
        print("Renaming %s -> %s" % (tmp_archive_name, dist_file))
        shutil.move(tmp_archive_name, dist_file)
