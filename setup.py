#!/usr/bin/env python
from __future__ import with_statement

import sys

try:
    from setuptools import setup, Extension, Command
except ImportError:
    from distutils.core import setup, Extension, Command

IS_PYPY = hasattr(sys, 'pypy_translation_info')
VERSION = '0.1'
DESCRIPTION = "A not so magical repository pattern with support for Django, SQLAlchemy (coming soon). And some pre-built middleware to make it ready out of the box."

class TestCommand(Command):
    nose_args = ['--with-coverage', '--cover-package=magicbox']
    user_options = []

    # If we run test just pass all arguments over to nosetest
    if sys.argv[1] == 'test' and len(sys.argv) > 2:
        nose_args = sys.argv[2:]
        sys.argv = sys.argv[:2]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import nose
        nose.run_exit(
                argv=["nosetests"] + self.nose_args
        )


def run_setup():
    cmdclass = dict(test=TestCommand)
    kw = dict(cmdclass=cmdclass)

    setup(
            name="magicbox",
            version=VERSION,
            description=DESCRIPTION,
            long_description=DESCRIPTION,
            classifiers=[
                "Operating System :: OS Independent",
                "Development Status :: 2 - Pre-Alpha",
                "Environment :: Web Environment",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python :: 3",
                "Topic :: Software Development :: Libraries :: Python Modules",
            ],
            author="Kirill Fuchs",
            author_email="kfuchs@fuzzproductions.com",
            license="MIT License",
            packages=['magicbox', 'tests'],
            platforms=['any'],
            **kw)


run_setup()
