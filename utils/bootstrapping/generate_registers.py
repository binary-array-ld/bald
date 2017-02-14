import json
from pprint import pprint
import rdflib
from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDF, DC, RDFS


with open('aliases.json') as data_file:
    data = json.load(data_file)


g = Graph()

NCLD_CLASS_str = "http://binary-array-ld.net/def/nc/classes/"
NCLD_VOCAB_str = "http://binary-array-ld.net/def/nc/vocab/"
NCLD_CLASS = Namespace(NCLD_CLASS_str) #Namespace TBC
NCLD_VOCAB = Namespace(NCLD_VOCAB_str) #Namespace TBC

g.bind("dc", DC)
g.bind("nc-class", NCLD_CLASS)
g.bind("nc-vocab", NCLD_VOCAB)

for key in data['names']:
    link = data['names'][key]
    subj = URIRef(NCLD_VOCAB_str + key)
    type = URIRef(NCLD_CLASS.Attribute)
    g.add( (subj, DC.identifier, Literal(key)) )
    g.add((subj, RDF.type, type))
    g.add((subj, RDFS.seeAlso, URIRef(link)))

print g.serialize(format='turtle')