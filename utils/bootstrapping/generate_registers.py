import json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, DC, RDFS,SKOS

with open('aliases.json') as data_file:
    data = json.load(data_file)

g = Graph()

NCLD_CLASS_str = "http://binary-array-ld.net/def/nc/classes/"
ACDD_NAMES_str = "http://binary-array-ld.net/def/acdd-names/"
CF_NAMES_str = "http://binary-array-ld.net/def/cf-names/"
NC_NAMES_str = "http://binary-array-ld.net/def/nc-names/"
CONVENTIONS_str = "http://binary-array-ld.net/def/conventions/"
UNKNOWN_str = "http://binary-array-ld.net/def/unknown-convention/"
NCLD_CLASS = Namespace(NCLD_CLASS_str) #Namespace TBC
ACDD_NAMES = Namespace(ACDD_NAMES_str) #Namespace TBC
NC_NAMES = Namespace(NC_NAMES_str) #Namespace TBC
CF_NAMES = Namespace(CF_NAMES_str) #Namespace TBC

g.bind("dc", DC)
g.bind("nc-class", NCLD_CLASS)
g.bind("cf-names", CF_NAMES)
g.bind("nc-names", NC_NAMES)
g.bind("skos", SKOS)
g.bind("acdd-names", ACDD_NAMES)

acdd_conv = URIRef(CONVENTIONS_str + "ACDD")
cf_conv = URIRef(CONVENTIONS_str + "CF")
nc_conv = URIRef(CONVENTIONS_str + "NetCDF")


g.add( (acdd_conv, RDF.type, SKOS.Collection))
g.add( (cf_conv, RDF.type, SKOS.Collection))
g.add( (nc_conv, RDF.type, SKOS.Collection))


for key in data['names']:
    link = data['names'][key]
    if(link.startswith("http://wiki.esipfed.org")):
        subj = URIRef(ACDD_NAMES_str + key)
        g.add((acdd_conv, SKOS.member, subj))
    elif(link.startswith("http://www.unidata.ucar.edu")):
        subj = URIRef(NC_NAMES_str + key)
        g.add((nc_conv, SKOS.member, subj))
    elif (link.startswith("http://cfconventions.org/cf-conventions/v1.6.0/")):
        subj = URIRef(CF_NAMES_str + key)
        g.add( (cf_conv, SKOS.member, subj))
    else:
        subj = URIRef(UNKNOWN_str + key)
    type = URIRef(NCLD_CLASS.Attribute)
    g.add( (subj, DC.identifier, Literal(key)) )
    g.add((subj, RDF.type, type))
    g.add((subj, RDFS.seeAlso, URIRef(link)))

print g.serialize(format='turtle')