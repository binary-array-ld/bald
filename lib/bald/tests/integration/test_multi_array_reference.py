import glob
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

    def test_validate_multi_array_reference(self):

        cdlfile = os.path.join(self.cdl_path, 'multi_array_reference.cdl')
        with self.temp_filename('.nc') as tfile:
            subprocess.check_call(['ncgen', '-o', tfile, cdlfile])
            validation = bald.validate_netcdf(tfile)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{} != []'.format(exns))

    def test_load(self):
        cdlfile = os.path.join(self.cdl_path, 'multi_array_reference.cdl')
        with self.temp_filename('.nc') as tfile:
            subprocess.check_call(['ncgen', '-o', tfile, cdlfile])
            inputs = bald.load_netcdf(tfile)
            set_collection = inputs.bald__contains[6].bald__references
            self.assertTrue(isinstance(set_collection, set))
            list_collection = inputs.bald__contains[7].bald__references
            self.assertTrue(isinstance(list_collection, list))

    def test_turtle(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'multi_array_reference.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            # with open(os.path.join(self.ttl_path, 'multi_array_reference.ttl'), 'w') as sf:
            #     sf.write(ttl)
            with open(os.path.join(self.ttl_path, 'multi_array_reference.ttl'), 'r') as sf:
                expected_ttl = sf.read()
            self.assertEqual(expected_ttl, ttl)



if __name__ == '__main__':
    unittest.main()
