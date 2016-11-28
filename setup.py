#!/usr/bin/env python
from __future__ import print_function

import os
from distutils.core import setup

DESCRIPTION = 'Binary Array Linked Data'
NAME = 'bald'
DIR_ROOT = os.path.abspath(os.path.dirname(__file__))
DIR_PACKAGE = os.path.join(DIR_ROOT, 'lib', NAME)


def extract_version():
    version = None
    fname = os.path.join(DIR_PACKAGE, '__init__.py')
    with open(fname) as fin:
        for line in fin:
            if (line.startswith('__version__')):
                _, version = line.split('=')
                version = version.strip()[1:-1]  # Remove quotation.
                break
    return version


def extract_description():
    description = DESCRIPTION
    fname = os.path.join(DIR_ROOT, 'README.rst')
    if os.path.isfile(fname):
        with open(fname) as fin:
            description = fin.read()
    return description


setup_args = dict(
    name=NAME,
    version=extract_version(),
    description=DESCRIPTION,
    long_description=extract_description(),
    platforms=['Linux', 'Max OS X', 'Windows'],
    license='BSD',
    url='https://github.com/binary-array-ld/bald',
    package_dir={'': 'lib'},
    packages=[NAME, '{}.tests'.format(NAME),
              '{}.tests.unit'.format(NAME),
              '{}.tests.integration'.format(NAME)],
    package_data={'{}.tests.integration'.format(NAME):
                  ['CDL/*.cdl', 'HTML/*.html', 'TTL/*.ttl']},
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 1 - Planning Development Status',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries'],
)


if __name__ == '__main__':
    setup(**setup_args)
