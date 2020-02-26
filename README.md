# Binary Array Linked Data: bald

[![Build Status](https://api.travis-ci.org/repositories/binary-array-ld/bald.svg?branch=master)](http://travis-ci.org/binary-array-ld/bald/branches)

A Python library for managing binary array linked data files.


## Parsing

This library processes payloads of various encodings and produces metadata graphs, in RDF, of the contents.  

Input payloads are provided with an identity, elements within the payload are identified, with respect to that payload identity, unless they are otherwise identified, by prefix or by alias.

Only Object values (attribute values) may be literals, consistent with the RDF interpretation. All Subjects and Predicates are identified with URIs. 

Some format specific implementation exists, due to the different capabilities available from different encodings.

### netCDF

For netCDF files, no variable to variable reference definitions are provided by the API.

For a variable to variable reference to be interpreted, an externally provided alias or predicate graph must explicitly state that a particular attribute has an rdfs:range of http://binary-array-ld.net/latest/Subject or a subclass of that class.

netCDF parsing is working to support the emerging draft Open Geospaatial Consortium approach to netCDF-Linked-Data: https://github.com/opengeospatial/netCDF-LD/

### HDF

HDF files and APIs have an object reference, indicating a reference from one element in the file to another.

These object refernces shall always be interpreted as references, regardless of the semantics of predicates (attribute names) provided by external graphs.


## Validation

This library provides some limited validation capabilities.

It is expected that a valid input payload will be able to be processed into a graph.  

Validation rules are limited in this implementation to require that provided HTTP URIs resolve.

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
$ conda install --quiet --file requirements.txt

```

Alternative steps using virtualenv and pip
```
virtualenv bald
source bald/bin/activate
pip install -r requirements.txt

```

## Quickstart

```
#install the bald module
$ python setup.py --quiet install

#running the tests
$ python -m unittest discover -s bald.tests -v
```

## Command line tools

### ncldDump

A HTML 'hot-linked' version of the `ncdump` command-line utility. 
The output of `ncldDump` is a something similar but with links to the standard names
and definitions of the attributes to source documentation. See https://binary-array-ld.github.io/netcdf-ld/examples/avhrr-only-v2.19810901_a.html for 
example output HTML.

See more here https://github.com/jyucsiro/bald/tree/master/ncldDump 

Getting started:
```
$ cd ncldDump
#Install requirements
$ pip install -r ../requirements.txt

#run
$ python ncldDump.py -a aliases.json -o test.html test.nc
```


### nc2rdf

A command-line tool that takes a netCDF or CDL file and outputs an RDF or JSON-LD encoding of the 
content. The RDF can then be imported into RDF triple stores or used with RDF libraries for 
reasoning, SPARQL querying and the like.

The RDFLib package is used so serialisation options to RDF are: `n3`, `nquads`, `nt`, `rdfxml`, `turtle` or `ttl`.

See more here https://github.com/jyucsiro/bald/tree/master/nc2rdf 

```
$ cd nc2rdf

# turn CDL into RDF
$ python nc2rdf.py  test.cdl

# turn NC into RDF
$ python nc2rdf.py  test.nc

# specify RDF formats/flavours 
$ python nc2rdf.py -o turtle test.nc

```


