import glob
import os
import subprocess
import unittest

import netCDF4
import numpy as np

import bald
from bald.tests import BaldTestCase
from rdflib import Graph


class Test(BaldTestCase):
    def setUp(self):
        self.cdl_path = os.path.join(os.path.dirname(__file__), 'CDL')
        self.ttl_path = os.path.join(os.path.dirname(__file__), 'TTL')
        self.graph = Graph()

        #load bald graphs from cdl
        for cdl_file in glob.glob(os.path.join(os.path.dirname(__file__), 'CDL', '*.cdl')):
            with self.temp_filename('.nc') as tfile:
               subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
               root_container = bald.load_netcdf(tfile)
               curr_g = root_container.rdfgraph()
 
            #merge into graph in test obj
            self.graph = self.graph  + curr_g

    def test_sparql_count_standard_names(self):
        #query standard_name values used and frequency
        qres = self.graph.query(
                    """ PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX bald:  <http://binary-array-ld.net/latest/>
                        SELECT ?name  (COUNT(?name) as ?NELEMENTS)
                        WHERE {
                           ?contained a bald:Array .  
                           ?contained ?pred ?name
                           FILTER(regex(str(?pred), "standard_name"))
                        }
                        GROUP BY ?name
                        ORDER BY DESC(?NELEMENTS)
                    """)
        for row in qres:
            print("%s :: %s" % row)
        print( len(qres))
        expected_result_rows = 15
        self.assertTrue(len(qres) == expected_result_rows)

    def test_sparql_demo_graph_viz_labels(self):
        #query standard_name values used and frequency
        qres = self.graph.query(
                 """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX bald:  <http://binary-array-ld.net/latest/>
                    PREFIX cf: <http://def.scitools.org.uk/CFTerms/>
                    SELECT ?container ?contained ?containerName ?containedlabel 
                    WHERE { 
                    ?container a bald:Container .  
                    ?container bald:contains ?contained .  
                    ?contained a bald:Array .  
                    { ?contained cf:long_name ?containedlabel } 
                    UNION 
                    { ?contained ?lnprop ?containedlabel 
                      FILTER(regex(str(?lnprop), "long_name", "i")) 
                    } 
                    BIND( str(?container) as ?containerName) }
                 """)
        for row in qres:
            print("%s, %s, %s, %s" % row)
        print( len(qres))
        expected_result_rows = 150
        self.assertTrue(len(qres) == expected_result_rows)

    def test_sparql_demo_map_viz_labels(self):
        #query standard_name values used and frequency
        qres = self.graph.query(
                 """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX bald:  <http://binary-array-ld.net/latest/>
                    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
                    SELECT ?contained ?geoWKT 
                    WHERE 
                    { 
                       ?container a bald:Container .  
                       ?container bald:contains ?contained .  
                       ?contained geo:asWKT ?geoWKT  
                    }
                 """)
        for row in qres:
            print("%s, %s" % row)
        print( len(qres))
        expected_result_rows = 2
        self.assertTrue(len(qres) == expected_result_rows)

