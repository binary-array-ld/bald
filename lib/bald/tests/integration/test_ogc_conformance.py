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
        
    def test_conformance_A(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'ogcClassA.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'http://secret.binary-array-ld.net/identity.nc'
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, 'ogcClassA.ttl'), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'ogcClassA.ttl'), 'r') as sf:
                expected_ttl = sf.read()
            self.assertEqual(expected_ttl, ttl)

    def test_conformance_b(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'ogcClassB.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'http://secret.binary-array-ld.net/prefix.nc'
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.ttl_path, 'ogcClassB.ttl'), 'w') as sf:
                    sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'ogcClassB.ttl'), 'r') as sf:
                expected_ttl = sf.read()
            self.assertEqual(expected_ttl, ttl)
