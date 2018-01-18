import os
import subprocess
import unittest

import netCDF4
import numpy as np

import bald
from bald.tests import BaldTestCase

class Test(BaldTestCase):
    def setUp(self):
        self.cdl_path = os.path.join(os.path.dirname(__file__), 'CDL')
        self.ttl_path = os.path.join(os.path.dirname(__file__), 'TTL')
        self.maxDiff = None
        
    def test_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'array_reference.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            # with open(os.path.join(self.ttl_path, 'array_reference.ttl'), 'w') as sf:
            #     sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'array_reference.ttl'), 'r') as sf:
                expected_ttl = sf.read()
            self.assertEqual(expected_ttl, ttl)

    def test_array_reference_with_baseuri(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'array_reference.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            root_container = bald.load_netcdf(tfile, baseuri='http://example.org/base', cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            #with open(os.path.join(self.ttl_path, 'array_reference_withbase.ttl'), 'w') as sf:
            #     sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'array_reference_withbase.ttl'), 'r') as sf:
                expected_ttl = sf.read()
            self.assertEqual(expected_ttl, ttl)

    def test_multi_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'multi_array_reference.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            # with open(os.path.join(self.ttl_path, 'multi_array_reference.ttl'), 'w') as sf:
            #     sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'multi_array_reference.ttl'), 'r') as sf:
                expected_ttl = sf.read()
            self.assertEqual(expected_ttl, ttl)

    def test_point_template(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'point_template.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            alias_dict = {'CFTerms': 'http://def.scitools.org.uk/CFTerms',
                          'cf_sname': 'http://vocab.nerc.ac.uk/standard_name/'
                         }
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            # with open(os.path.join(self.ttl_path, 'point_template.ttl'), 'w') as sf:
            #     sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'point_template.ttl'), 'r') as sf:
                expected_ttl = sf.read()
            self.assertEqual(expected_ttl, ttl)

    def test_gems_co2(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'GEMS_CO2_Apr2006.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            alias_dict = {'CFTerms': 'http://def.scitools.org.uk/CFTerms',
                          'cf_sname': 'http://vocab.nerc.ac.uk/standard_name/'
                         }
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            # with open(os.path.join(self.ttl_path, 'GEMS_CO2_Apr2006.ttl'), 'w') as sf:
            #     sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'GEMS_CO2_Apr2006.ttl'), 'r') as sf:
                expected_ttl = sf.read()
            self.assertEqual(expected_ttl, ttl)

    def test_ereefs(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'ereefs_gbr4_ncld.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            root_container = bald.load_netcdf(tfile, cache=self.acache)
            try:
               g  = root_container.rdfgraph()
               ttl = g.serialize(format='n3').decode("utf-8")
            except TypeError:
               self.fail("Test case could not convert ereefs CDL to RDF")

