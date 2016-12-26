"""Conda-related utilities."""
import distutils.log
import platform
import subprocess
import sys

import os
import tempfile

if sys.version_info[0] > 2:
    import urllib.request as urllib
else:
    import urllib

CONDA_BASH_FILENAME = 'conda.sh'

if platform.system() == 'Darwin':
    DEFAULT_CONDA_URL = 'https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh'
elif platform.system() == 'Linux':
    DEFAULT_CONDA_URL = 'https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh'
else:
    raise RuntimeError("Unsupported platform: %s" % platform.system())


def install_conda(command):
    """Install conda."""
    tmpdir = tempfile.mkdtemp()
    target = os.path.join(tmpdir, 'conda.sh')
    command.announce("Fetching %s -> %s" % (command.conda_url, target), level=distutils.log.INFO)
    urllib.urlretrieve(command.conda_url, target)
    subprocess.check_call("bash {conda_sh} -p {prefix} -f -b".format(
        conda_sh=target,
        prefix=command.conda_install_path), shell=True)
    return os.path.join(command.conda_install_path, 'bin', 'conda')
