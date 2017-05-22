from __future__ import unicode_literals
import json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, DCTERMS, RDFS,SKOS, OWL

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


DEFSCIT_str = "http://def.scitools.org.uk/"

NCLD_CLASS_str = "http://def.scitools.org.uk/NCClasses/"
ACDD_NAMES_str = "http://def.scitools.org.uk/ACDD/"
CF_NAMES_str = "http://def.scitools.org.uk/CFTerms/"
#OP_NAMES_str = "http://binary-array-ld.net/def/op-names/"
NC_NAMES_str = "http://def.scitools.org.uk/NetCDF/"
CONVENTIONS_str = "http://def.scitools.org.uk/def/conventions/"
#OP_str = "http://binary-array-ld.net/def/conventions/"
#UNKNOWN_str = "http://binary-array-ld.net/def/unknown-convention/"
# NCLD_CLASS = Namespace(NCLD_CLASS_str) #Namespace TBC
ACDD_NAMES = Namespace(ACDD_NAMES_str) #Namespace TBC
NC_NAMES = Namespace(NC_NAMES_str) #Namespace TBC
CF_NAMES = Namespace(CF_NAMES_str)
DEFSCIT_NAMES = Namespace(DEFSCIT_str)

REG_str = "http://purl.org/linked-data/registry#"
REG_NAMES = Namespace(REG_str)

g1.bind("dc", DCTERMS)
g1.bind("skos", SKOS)
g1.bind("acdd-names", ACDD_NAMES)

g2.bind("dc", DCTERMS)
g2.bind("skos", SKOS)
g2.bind("nc-names", NC_NAMES)

g3.bind("dc", DCTERMS)
g3.bind("skos", SKOS)
g3.bind("cf-names", CF_NAMES)
g3.bind("defscit", DEFSCIT_NAMES)
g3.bind("reg", REG_NAMES)

op_conv = URIRef(CONVENTIONS_str + "op")

# define collections
#acdd_conv = URIRef(DEFSCIT_str + "ACDD")
#g1.add((acdd_conv, RDF.type, SKOS.Collection))
#g1.add((acdd_conv, RDFS.label, Literal("ACDD")))
#g1.add((acdd_conv, DCTERMS.description, Literal("Vocabulary of terms used in the Attribute Conventions Dataset Discovery Vocabulary.")))
#g1.add((acdd_conv, URIRef(REG_str + "category"), URIRef("http://def.scitools.org.uk/structure/category/SciTools")))


#nc_conv = URIRef(DEFSCIT_str + "NetCDF")
#g2.add((nc_conv, RDF.type, SKOS.Collection))
#g2.add((nc_conv, RDFS.label, Literal("NetCDF")))
#g2.add((nc_conv, DCTERMS.description, Literal("Vocabulary of terms used in the netCDF User Guide.")))
#g2.add((nc_conv, URIRef(REG_str + "category"), URIRef("http://def.scitools.org.uk/structure/category/SciTools")))


#cfcol = URIRef(DEFSCIT_str + "CFTerms")
#g3.add( (cfcol, RDF.type, SKOS.Collection))
#g3.add((cfcol, RDFS.label, Literal("CFTerms")))
#g3.add((cfcol, DCTERMS.description, Literal("Vocabulary of terms used in the CF conventions for netCDF files.")))
#g3.add((cfcol, URIRef(REG_str + "category"), URIRef("http://def.scitools.org.uk/structure/category/SciTools")))

for key in data['names']:
    link = data['names'][key]

    if(link.startswith("http://wiki.esipfed.org")):
        subj = URIRef(DEFSCIT_str + "ACDD/" + key)
        #g1.add((acdd_conv, SKOS.member, subj))
        #g1.add((subj, RDF.type, SKOS.Concept))
        g1.add((subj, RDF.type, RDF.Property))
        g1.add((subj, DCTERMS.identifier, Literal(key)))
        g1.add((subj, RDFS.label, Literal(key)))
        g1.add((subj, RDFS.seeAlso, URIRef(cleanup_link(link))))

    elif(link.startswith("http://www.unidata.ucar.edu")):
        # can't have '_' as a leading character in a resource identified: LDReg rules
        subj = URIRef(NC_NAMES_str + key.replace('_', ''))
        #g2.add((nc_conv, SKOS.member, subj))
        #g2.add((subj, RDF.type, SKOS.Concept))
        g2.add((subj, RDF.type, RDF.Property))
        g2.add((subj, DCTERMS.identifier, Literal(key)))
        g2.add((subj, RDFS.label, Literal(key)))
        g2.add((subj, RDFS.seeAlso, URIRef(cleanup_link(link))))

    elif (link.startswith("http://cfconventions.org/cf-conventions/v1.6.0/")):
        subj = URIRef(DEFSCIT_str + "CFTerms/" + key)
        #g3.add((cfcol, SKOS.member, subj))
        #g3.add((subj, RDF.type, SKOS.Concept))
        g3.add((subj, RDF.type, RDF.Property))
        g3.add((subj, DCTERMS.identifier, Literal(key)))
        g3.add((subj, RDFS.label, Literal(key)))
        g3.add((subj, RDFS.seeAlso, URIRef(cleanup_link(link))))

    # elif (link.startswith("http://environment.data.gov.au/def/op")):
    #     subj = URIRef(OP_NAMES_str + key)
    #     g5.add( (op_conv, SKOS.member, subj))
    #     g5.add((subj, DCTERMS.identifier, Literal(key)))
    #     g4.add((subj, RDFS.label, Literal(key)))
    #     g5.add((subj, RDFS.seeAlso, URIRef(cleanup_link(link))))
    # else:
    #     subj = URIRef(UNKNOWN_str + key)
    #     g4.add((subj, DCTERMS.identifier, Literal(key)))
    #     g4.add((subj, RDFS.label, Literal(key)))
    #     g4.add((subj, RDFS.seeAlso, URIRef(cleanup_link(link))))


print 'emiting acdd.ttl'
g1.serialize('acdd.ttl', format='turtle')
print 'emiting nc-names.ttl'
g2.serialize('nc-names.ttl', format='turtle')
print 'emiting cf-names.ttl'
g3.serialize('cf-names.ttl', format='turtle')
# print 'emiting op.ttl'
# g5.serialize('op-names.ttl', format='turtle')
# print 'emiting unknown.ttl'
# g4.serialize('unknown.ttl', format='turtle')
