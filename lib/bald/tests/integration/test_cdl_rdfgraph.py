import itertools
import json
import os
import subprocess
import unittest

import netCDF4
import numpy as np
import rdflib
import rdflib.compare
import requests

import bald
from bald.tests import BaldTestCase

class Test(BaldTestCase):
    def setUp(self):
        self.cdl_path = os.path.join(os.path.dirname(__file__), 'CDL')
        self.ttl_path = os.path.join(os.path.dirname(__file__), 'TTL')
        self.maxDiff = None

    def check_result(self, result, expected):
        lbb = ('\n#######inBothResults#######\n')
        lbr = ('\n#######inTestResult#######\n')
        lbe = ('\n#######inExpected#######\n')
        lb = [lbb, lbr, lbe]

        self.assertTrue(rdflib.compare.isomorphic(result, expected),
                        ''.join(list(itertools.chain(*zip(lb, [g.serialize(format='n3').decode("utf-8") for g in
                                        rdflib.compare.graph_diff(result,
                                                                  # expected)[1:]]))
                                                                  expected)])))))
                                 
                        # lbr + lbe.join([g.serialize(format='n3').decode("utf-8") for g in
                        #                 rdflib.compare.graph_diff(result,
                        #                                           # expected)[1:]]))
                        #                                           expected)]))

        
    def test_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'array_reference.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, cache=self.acache)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, 'array_reference.ttl'), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'array_reference.ttl'), 'r') as sf:
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)
                
    def test_array_reference_with_baseuri(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'array_reference.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            root_container = bald.load_netcdf(tfile, baseuri='http://example.org/base', cache=self.acache)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, 'array_reference_withbase.ttl'), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'array_reference_withbase.ttl'), 'r') as sf:
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)

    def test_array_reference_external_prefix_context(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'array_reference_external_prefix_context.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            prefix_context = json.dumps({'@context': {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                                                      'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                                                      'bald': 'https://www.opengis.net/def/binary-array-ld/'}})
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, prefix_contexts=prefix_context,
                                              cache=self.acache)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, 'array_reference_external_prefix_context.ttl'), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'array_reference_external_prefix_context.ttl'), 'r') as sf:
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)

    def test_multi_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'multi_array_reference.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, cache=self.acache)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, 'multi_array_reference.ttl'), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'multi_array_reference.ttl'), 'r') as sf:
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)

    def test_point_template(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'point_template.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            alias_dict = {'NetCDF': 'http://def.scitools.org.uk/NetCDF',
                          'CFTerms': 'http://def.scitools.org.uk/CFTerms',
                          'cf_sname': 'http://vocab.nerc.ac.uk/standard_name/'
                         }
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, 'point_template.ttl'), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'point_template.ttl'), 'r') as sf:
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)

    def test_gems_co2(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'GEMS_CO2_Apr2006.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            alias_dict = {'NetCDF': 'http://def.scitools.org.uk/NetCDF',
                          'CFTerms': 'http://def.scitools.org.uk/CFTerms',
                          'cf_sname': 'http://vocab.nerc.ac.uk/standard_name/'
                         }
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, 'GEMS_CO2_Apr2006.ttl'), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'GEMS_CO2_Apr2006.ttl'), 'r') as sf:
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)

    def test_ProcessChain0300(self):
        with self.temp_filename('.nc') as tfile:
            name = 'ProcessChain0300'
            cdl_file = os.path.join(self.cdl_path, '{}.cdl'.format(name))
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}.cdl'.format(name)
            alias_dict = {'CFTerms': 'http://def.scitools.org.uk/CFTerms',
                          'cf_sname': 'http://vocab.nerc.ac.uk/standard_name/'
                         }
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, '{}.ttl'.format(name)), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, '{}.ttl'.format(name)), 'r') as sf:
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)

    def test_ereefs(self):
        with self.temp_filename('.nc') as tfile:
            name = 'ereefs_gbr4_ncld'
            cdl_file = os.path.join(self.cdl_path, '{}.cdl'.format(name))
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}.cdl'.format(name)
            alias_dict = {'NetCDF': 'http://def.scitools.org.uk/NetCDF',
                          'CFTerms': 'http://def.scitools.org.uk/CFTerms',
                          'cf_sname': 'http://vocab.nerc.ac.uk/standard_name/'
                         }
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, '{}.ttl'.format(name)), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, '{}.ttl'.format(name)), 'r') as sf:
                # expected_ttl = sf.read()
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)

    def test_votemper(self):
        with self.temp_filename('.nc') as tfile:
            name = 'votemper'
            cdl_file = os.path.join(self.cdl_path, '{}.cdl'.format(name))
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}.cdl'.format(name)
            alias_dict = {'NetCDF': 'http://def.scitools.org.uk/NetCDF',
                          'CFTerms': 'http://def.scitools.org.uk/CFTerms',
                          'cf_sname': 'http://vocab.nerc.ac.uk/standard_name/'
                         }
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, '{}.ttl'.format(name)), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, '{}.ttl'.format(name)), 'r') as sf:
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)

    def test_hgroups(self):
        with self.temp_filename('.nc') as tfile:
            name = 'hgroups'
            hgurl = 'https://www.unidata.ucar.edu/software/netcdf/examples/test_hgroups.cdl'
            res = requests.get(hgurl)
            if res.status_code != 200:
                raise ValueError('{} failed to download: {}'.format(hgurl, res.status_code))
            with self.temp_filename('.cdl.') as cdlfile:
                with open(cdlfile, 'w') as fh:
                    fh.write(res.text)
                #cdl_file = os.path.join(self.cdl_path, '{}.cdl'.format(name))
                subprocess.check_call(['ncgen', '-o', tfile, cdlfile])
            cdl_file_uri = 'file://CDL/{}.cdl'.format(name)
            alias_dict = {'NetCDF': 'http://def.scitools.org.uk/NetCDF',
                          'CFTerms': 'http://def.scitools.org.uk/CFTerms',
                          'cf_sname': 'http://vocab.nerc.ac.uk/standard_name/'
                         }
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache, file_locator=hgurl)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, '{}.ttl'.format(name)), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, '{}.ttl'.format(name)), 'r') as sf:
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)
            
    def test_group_array_geo(self):
        with self.temp_filename('.nc') as tfile:
            name = 'group_array_geo'
            # hgurl = 'https://www.unidata.ucar.edu/software/netcdf/examples/test_hgroups.cdl'
            # res = requests.get(hgurl)
            # if res.status_code != 200:
            #     raise ValueError('{} failed to download: {}'.format(hgurl, res.status_code))
            # with self.temp_filename('.cdl.') as cdlfile:
            #     with open(cdlfile, 'w') as fh:
            #         fh.write(res.text)
            cdl_file = os.path.join(self.cdl_path, '{}.cdl'.format(name))
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}.cdl'.format(name)
            alias_dict = {# 'NetCDF': 'http://def.scitools.org.uk/NetCDF',
                          # 'CFTerms': 'http://def.scitools.org.uk/CFTerms',
                          'cf_sname': 'http://vocab.nerc.ac.uk/standard_name/'
                         }
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache)
            rdfgraph = root_container.rdfgraph()
            ttl = rdfgraph.serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, '{}.ttl'.format(name)), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, '{}.ttl'.format(name)), 'r') as sf:
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(sf, format='n3')
            self.check_result(rdfgraph, expected_rdfgraph)
            
