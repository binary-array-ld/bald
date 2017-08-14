# nc2rdf

This tool allows users to input CDL or netCDF files and get an RDF graph returned.

Example:
```
$ python nc2rdf.py  ../lib/bald/tests/integration/CDL/array_alias.cdl
```

By default, nc2rdf tries to detect CDL and nc files using the file suffix. Output by default is
RDF N3 triples.

Users can specify CDL files using the `--cdl` option.
```
$ python nc2rdf.py --cdl myfile.cdl
```

Users can specify netCDF files usings the `--nc` ioption.
```
$ python nc2rdf.py --nc myfile.nc
```

More info, refer to the help option
```
$ python nc2rdf.py -h
```

Other outputs include TTL and XML
```
$ python nc2rdf.py -o ttl myfile.nc
$ python nc2rdf.py -o xml myfile.nc
```

Note: This command-line tool is experimental and is subject to changes, however serves as a prototype for accessing bald functions for netCDF related files to RDF.
