# Binary Array Linked Data: bald

[![Build Status](https://api.travis-ci.org/repositories/binary-array-ld/bald.svg?branch=master)](http://travis-ci.org/binary-array-ld/bald/branches)

A Python library for validating and managing binary array linked data files.

## Pre-requisites

* netCDF - see https://gist.github.com/perrette/cd815d03830b53e24c82 for installing on Ubuntu
* python 3
* miniconda

Suggested configuration steps
```
conda create -n ncld-bald
conda config --add channels conda-forge
conda config --add channels bioconda
conda config --set show_channel_urls True
source activate ncld-bald
```

## Quickstart

```
#install required modules
$ conda install --quiet --file requirements.txt

#install the bald module
$ python setup.py --quiet install

#running the tests
$ python -m unittest discover -s bald.tests -v
```
