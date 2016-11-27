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
        
    def test_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'array_reference.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            root_container = bald.load_netcdf(tfile)
            ttl = root_container.rdfgraph().serialize(format='n3')
            # with open(os.path.join(self.ttl_path, 'array_reference.ttl'), 'w') as sf:
            #     sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'array_reference.ttl'), 'r') as sf:
                expected_ttl = sf.read()
            self.assertEqual(expected_ttl, ttl)

    def test_multi_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'multi_array_reference.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            root_container = bald.load_netcdf(tfile)
            ttl = root_container.rdfgraph().serialize(format='n3')
            # with open(os.path.join(self.ttl_path, 'multi_array_reference.ttl'), 'w') as sf:
            #     sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'multi_array_reference.ttl'), 'r') as sf:
                expected_ttl = sf.read()
            self.assertEqual(expected_ttl, ttl)
