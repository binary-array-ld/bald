#!/usr/bin/env python
from __future__ import print_function

import os
from setuptools import setup


DESCRIPTION = 'Binary Array Linked Data'
NAME = 'bald'
DIR_ROOT = os.path.abspath(os.path.dirname(__file__))
DIR_PACKAGE = os.path.join(DIR_ROOT, 'lib', NAME)
#DIR_DATA = os.path.join(DIR_PACKAGE, 'sample_data')


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


# def extract_package_data():
#     package_data = []
#     offset = len(os.path.dirname(DIR_DATA)) + 1
#     for dpath, dnames, fnames in os.walk(DIR_DATA):
#         globs = set()
#         fpath = os.path.join(dpath[offset:])
#         for fname in fnames:
#             _, ext = os.path.splitext(fname)
#             globs.add('*{}'.format(ext))
#         for glob in globs:
#             package_data.append(os.path.join(fpath, glob))
#     return {NAME: package_data}


setup_args = dict(
    name=NAME,
    version=extract_version(),
    description=DESCRIPTION,
    long_description=extract_description(),
    platforms=['Linux', 'Max OS X', 'Windows'],
    license='BSD',
    url='https://github.com/binary-array-ld/bald',
    package_dir={'': 'lib'},
    packages=[NAME],
    # package_data=extract_package_data(),
    classifiers=[
        # For full license details, see
        # http://reference.data.gov.uk/id/open-government-licence
        'License :: Freely Distributable',
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
