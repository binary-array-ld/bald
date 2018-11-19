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



def getBasename(urlstr):
   return os.path.basename(urlstr)

def baldgraph2schemaorg(graph):
    """
       Input: netCDF file
       Transforms to a rdflib.Graph bald style
       Returns a new graph in schema.org profile
    """
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
    container = BNode()
    so = Namespace("http://schema.org/")
    schema_g.add( (container, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), so.Dataset) )

    for row in qres:
       currField = getBasename(str(row[0])).strip()
       #print(getBasename(str(row[0])) + ' (type: ' + str(type(row[0])) + ")" + " :: " + row[1] + ' (type: ' + str(type(row[1])) + ")")
       if(currField in mapping_idx.keys()):
          print('schemaorg:' + mapping_idx[currField], "\t", row[1])
          predUri = URIRef("http://schema.org/" + mapping_idx[currField])
          lit = Literal(row[1])
          schema_g.add( (container, predUri, lit) )
    return schema_g

def nc2schemaorg(ncfilename, outformat, baseuri=None):
    root_container = bald.load_netcdf(ncfilename, baseuri=baseuri)
    graph = root_container.rdfgraph()
    schema_g = baldgraph2schemaorg(graph)
    
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
