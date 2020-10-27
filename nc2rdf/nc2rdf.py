import argparse
import os
import subprocess
import tempfile 
import netCDF4
import numpy as np
import bald
import rdflib
import json
from rdflib import Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF
try:
    # python 3
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

def isUrl(url):
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc, result.path]) and (result.scheme == 'https' or result.scheme == 'http'):
           return True
    except:
        return False

def getBasename(urlstr):
   return os.path.basename(urlstr)

def baldgraph2schemaorg(graph, path=None, baseuri=None):
    """
       Input: netCDF file
       Transforms to a rdflib.Graph bald style
       Returns a new graph in schema.org profile
    """
    # HACK: The following mappings ignore prefixes as well as prefixes in nc file
    # TODO: Fix references to prefixes/aliases proper

    #encoding formats to use - one as Text, one as URL
    encodingFormats = ["application/x-netcdf",
                       "http://vocab.nerc.ac.uk/collection/M01/current/NC/"]

    #load mappings
    mapping_idx = {}
    mapping_data = []
    with open('bald2schemaorg_mappings.json' , 'r') as f:
       mapping_data = json.load(f)
       
    for item in mapping_data:
       mapping_idx[item['bald']] = item['schemaorg']

    qres = graph.query(
    """PREFIX bald: <http://binary-array-ld.net/latest/> 
       SELECT DISTINCT ?pred ?value
       WHERE {
          ?c a bald:Container .
          ?c ?pred ?value
       }""")
 
    schema_g = rdflib.Graph()

    if baseuri is not None:
       container = URIRef(baseuri)
    else:
       container = BNode()

    so = Namespace("http://schema.org/")
    schema_g.add( (container, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), so.Dataset) )

    if path is not None and isUrl(path):
       predUri = URIRef("http://schema.org/url")
       schema_g.add( (container, predUri, URIRef(path)) )

    for row in qres:
       currField = getBasename(str(row[0])).strip()
       #print(getBasename(str(row[0])) + ' (type: ' + str(type(row[0])) + ")" + " :: " + row[1] + ' (type: ' + str(type(row[1])) + ")")
       if(currField in mapping_idx.keys()):
          predUri = URIRef("http://schema.org/" + mapping_idx[currField])
          if currField == 'keywords':
             for x in row[1].split(','):
                kw = x.strip()
                if len(kw) == 0:
                   continue
                lit = Literal(kw)
                schema_g.add( (container, predUri, lit) )
             continue

          #print('schemaorg:' + mapping_idx[currField], "\t", row[1])
          lit = Literal(row[1])
          schema_g.add( (container, predUri, lit) )
    #
    # Add some distrbution details
    #
    schema_org_inst  =  bald.schemaOrg()
    schema_g  =  schema_org_inst.distribution(container, schema_g, baseuri)
    return schema_g

def nc2schemaorg(ncfilename, outformat, baseuri=None):
    root_container = bald.load_netcdf(ncfilename, baseuri=baseuri)
    graph = root_container.rdfgraph()
    schema_g = baldgraph2schemaorg(graph, path=ncfilename, baseuri=baseuri)
    
    if(outformat == 'json-ld'):
       context = "http://schema.org/"
       s = schema_g.serialize(format=outformat, context=context, indent=4).decode("utf-8")
    else:
       s = schema_g.serialize(format=outformat).decode("utf-8")
    print(s)

def nc2rdf(ncfilename, outformat, baseuri=None):  
    root_container = bald.load_netcdf(ncfilename, baseuri=baseuri)
    ttl = root_container.rdfgraph().serialize(format=outformat).decode("utf-8")
    print(ttl)

def cdl2schemaorg(cdl_file, outformat, baseuri=None): 
    tfile, tfilename = tempfile.mkstemp('.nc')
    subprocess.check_call(['ncgen', '-o', tfilename, cdl_file])
    schema_g = nc2schemaorg(tfilename, outformat, baseuri=baseuri)
    os.close(tfile)
    os.remove(tfilename)
    return schema_g

def cdl2rdf(cdl_file, outformat, baseuri=None): 
    #print("cdl2rdf test")
    #print(cdl_file)
    tfile, tfilename = tempfile.mkstemp('.nc')
    #print(tfilename)
    subprocess.check_call(['ncgen', '-o', tfilename, cdl_file])

    nc2rdf(tfilename, outformat, baseuri=baseuri)

    os.close(tfile)
    os.remove(tfilename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert netCDF metadata to RDF.')
    parser.add_argument('-o', action="store", dest="format", default='n3', help="RDF output format (n3 *default, ttl, xml)")
    parser.add_argument('--baseuri', action="store", dest="baseuri", help="Base URI for the graph")
    parser.add_argument('--cdl', action="store_true", dest="isCDL", default=False, help="Flag to indicate file is CDL")
    parser.add_argument('--nc', action="store_true", dest="isNC", default=False, help="Flag to indicate file is netCDF")
    parser.add_argument('--schema-org', action="store_true", dest="isSchemaOrgOutput", default=False, help="Flag to indicate if schema.org output activated")
    parser.add_argument("ncfile", help="Path for the netCDF file")

    args = parser.parse_args()

    if(args.isCDL or args.ncfile.endswith(".cdl") or args.ncfile.endswith('.CDL')):
        if(args.isSchemaOrgOutput):
           cdl2schemaorg(args.ncfile, args.format, baseuri=args.baseuri)
        else:
           cdl2rdf(args.ncfile, args.format, baseuri=args.baseuri)
    elif(args.isNC or args.ncfile.endswith(".nc") or args.ncfile.endswith('.NC')):
        if(args.isSchemaOrgOutput):
           nc2schemaorg(args.ncfile, args.format, baseuri=args.baseuri)
        else:
           nc2rdf(args.ncfile, args.format, baseuri=args.baseuri)
    else:
        print("Unrecognised file suffix. Please indicate if CDL or NC via --cdl or --nc");
