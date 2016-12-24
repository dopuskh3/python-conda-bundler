import subprocess
import urllib
import tempfile
import os

def install_conda(cond_distribution_url):
    tmpdir = tempfile.mkdtemp()
    urllib.urlretrieve(cond_distribution_url, os.path.join(tmpdir, 'conda.sh'))
