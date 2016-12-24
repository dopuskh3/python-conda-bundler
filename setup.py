#!/usr/bin/env python3
from distutils.core import setup

import setuptools

setup(name="python-bundler",
      version='0.1',
      install_requires=[
      ],
      test_requires=[],
      entry_points={
          "distutils.commands": [
              "bdist_conda=bundler.bundler_cmd:BundleCommand"]

      },
      packages=setuptools.find_packages())
