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
        print(self.cdl_path)
        
    def test_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'array_reference.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            validation = bald.validate_netcdf(tfile)
            self.assertTrue(validation.is_valid())

    def test_alias(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'array_alias.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            validation = bald.validate_netcdf(tfile)
            self.assertTrue(validation.is_valid())
