[![Build Status](https://travis-ci.org/dopuskh3/python-bundler.svg?branch=master)](https://travis-ci.org/dopuskh3/python-bundler)
[![Coverage Status](https://coveralls.io/repos/github/dopuskh3/python-bundler/badge.svg?branch=master)](https://coveralls.io/github/dopuskh3/python-bundler?branch=master)
[![Dependency Status](https://gemnasium.com/badges/github.com/dopuskh3/python-bundler.svg)](https://gemnasium.com/github.com/dopuskh3/python-bundler)

#Python-conda-bundler

This package installs a distutils command that bundle python package into a self contained conda bundle.

## bdist_conda options:

* `--conda-packages=`: a list of conda package specification to install in env
* `--conda-url=`: Miniconda shell scritp distribution URL
* `--conda-bin=`: Conda command to invoke (default `conda`)
* `--conda-install-path=`: conda install path if `--conda-url=` is specified

Note that options can also be specified in `setup.cfg` file:

~~~~
[bdist_conda]
conda-packages=foo,bar,bazz
conda-url=file:///also/support/for/file/urls.sh
cona-instal-path=/tmp/conda-install-path
~~~~

## Testing

Install tox and run:

```
  $ tox
```
