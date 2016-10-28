The ncldDump application requires the python packages jinja2, netCDF4, and
numpy.

To see how to run the application, run it with a single '-h' argument.

In this initial version there is no attempt to find alias information inside
the netCDF file being dumped. All context and alias definitions are found in
the JSON alias file that is specified to the application using the -a argument.

The aliases.json file is a working example. It is currently populated with
aliases for all CF attribute names and for certain attribute values. If a
dictionary key in the "values" section is '*', this indicates that any
attribute value for the parent attribute name will produce a match. All items
in the dictionary can be treated as patterns that can have a python '{}'
element. This element will be replaced by the key value. (If the key is '*'
then the attribute value will treated as the key value.)

The initial version of the application has a placeholder in the aliases.json
file for context definitions, but the code does not yet recognize or use them.
