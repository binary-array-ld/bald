from __future__ import unicode_literals
import json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, DC, RDFS,SKOS

def cleanup_link(link):
    newlink = link
    if(link.find('{}')):
        newlink = link.replace("{}", "")

    return newlink

with open('../../ncldDump/aliases.json') as data_file:
    data = json.load(data_file)

g1 = Graph()
g2 = Graph()
g3 = Graph()
g4 = Graph()
g5 = Graph()

NCLD_CLASS_str = "http://def.scitools.org.uk/NCClasses/"
ACDD_NAMES_str = "http://def.scitools.org.uk/ACDD/"
CF_NAMES_str = "http://def.scitools.org.uk/CFTerms/"
OP_NAMES_str = "http://binary-array-ld.net/def/op-names/"
NC_NAMES_str = "http://binary-array-ld.net/def/nc-names/"
CONVENTIONS_str = "http://def.scitools.org.uk/def/conventions/"
OP_str = "http://binary-array-ld.net/def/conventions/"
UNKNOWN_str = "http://binary-array-ld.net/def/unknown-convention/"
NCLD_CLASS = Namespace(NCLD_CLASS_str) #Namespace TBC
ACDD_NAMES = Namespace(ACDD_NAMES_str) #Namespace TBC
NC_NAMES = Namespace(NC_NAMES_str) #Namespace TBC
CF_NAMES = Namespace(CF_NAMES_str) #Namespace TBC

g1.bind("dc", DC)
g1.bind("nc-class", NCLD_CLASS)
g1.bind("skos", SKOS)
g1.bind("acdd-names", ACDD_NAMES)

g2.bind("dc", DC)
g2.bind("nc-class", NCLD_CLASS)
g2.bind("skos", SKOS)
g2.bind("nc-names", NC_NAMES)

g3.bind("dc", DC)
g3.bind("nc-class", NCLD_CLASS)
g3.bind("skos", SKOS)
g3.bind("cf-names", CF_NAMES)


#g.bind("dc", DC)
#g.bind("nc-class", NCLD_CLASS)
#g.bind("cf-names", CF_NAMES)
#g.bind("nc-names", NC_NAMES)
#g.bind("skos", SKOS)
#g.bind("acdd-names", ACDD_NAMES)



acdd_conv = URIRef(CONVENTIONS_str + "ACDD")
cf_conv = URIRef(CONVENTIONS_str + "CF")
nc_conv = URIRef(CONVENTIONS_str + "NetCDF")
op_conv = URIRef(CONVENTIONS_str + "op")


g1.add( (acdd_conv, RDF.type, SKOS.Collection))
g2.add( (nc_conv, RDF.type, SKOS.Collection))
g3.add( (cf_conv, RDF.type, SKOS.Collection))


for key in data['names']:
    link = data['names'][key]
    type = URIRef(NCLD_CLASS.Attribute)

    if(link.startswith("http://wiki.esipfed.org")):
        subj = URIRef(ACDD_NAMES_str + key)
        g1.add((acdd_conv, SKOS.member, subj))
        g1.add((subj, DC.identifier, Literal(key)))
        g1.add((subj, RDF.type, type))
        g1.add((subj, RDFS.seeAlso, URIRef(cleanup_link(link))))
    elif(link.startswith("http://www.unidata.ucar.edu")):
        subj = URIRef(NC_NAMES_str + key)
        g2.add((nc_conv, SKOS.member, subj))
        g2.add((subj, DC.identifier, Literal(key)))
        g2.add((subj, RDF.type, type))
        g2.add((subj, RDFS.seeAlso, URIRef(cleanup_link(link))))
    elif (link.startswith("http://cfconventions.org/cf-conventions/v1.6.0/")):
        subj = URIRef(CF_NAMES_str + key)
        g3.add( (cf_conv, SKOS.member, subj))
        g3.add((subj, DC.identifier, Literal(key)))
        g3.add((subj, RDF.type, type))
        g3.add((subj, RDFS.seeAlso, URIRef(cleanup_link(link))))
    elif (link.startswith("http://environment.data.gov.au/def/op")):
        subj = URIRef(OP_NAMES_str + key)
        g5.add( (op_conv, SKOS.member, subj))
        g5.add((subj, DC.identifier, Literal(key)))
        g5.add((subj, RDF.type, type))
        g5.add((subj, RDFS.seeAlso, URIRef(cleanup_link(link))))
    else:
        subj = URIRef(UNKNOWN_str + key)
        g4.add((subj, DC.identifier, Literal(key)))
        g4.add((subj, RDF.type, type))
        g4.add((subj, RDFS.seeAlso, URIRef(cleanup_link(link))))


print 'emiting acdd.ttl'
g1.serialize('acdd.ttl', format='turtle')
print 'emiting nc-names.ttl'
g2.serialize('nc-names.ttl', format='turtle')
print 'emiting cf-names.ttl'
g3.serialize('cf-names.ttl', format='turtle')
print 'emiting op.ttl'
g5.serialize('op-names.ttl', format='turtle')
print 'emiting unknown.ttl'
g4.serialize('unknown.ttl', format='turtle')