#!/usr/bin/env python
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

# This is needed to run unit from within pytest like when called from shell


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='nord-pool-api',
    version='0.0.1',
    description='Nord Pool (Backend)',
    author='Trading IT Dev',
    author_email='developers@trading.ewe.info',
    packages=find_packages(
        exclude=['*.tests', '*.tests.*', 'tests.*', 'tests', ]),
    cmdclass={'test': PyTest}, install_requires=['base']
)
