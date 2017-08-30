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


def test_prefix_v2(self):
    """Test prefix version 2 style """
    with self.temp_filename('.nc') as tfile:
        cdl_file = os.path.join(self.cdl_path, 'array_prefix_v2.cdl')
        print(cdl_file)
        subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
        validation = bald.validate_netcdf(tfile)
        exns = validation.exceptions()
        self.assertTrue(validation.is_valid(), msg='{} != []'.format(exns))

setattr(Test, 'test_prefix_v2', test_prefix_v2)

def test_prefix_v2_full(self):
    """Test prefix version 2 style - full example"""
    with self.temp_filename('.nc') as tfile:
        cdl_file = os.path.join(self.cdl_path, 'array_prefix_v2_full.cdl')
        print(cdl_file)
        subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
        validation = bald.validate_netcdf(tfile)
        exns = validation.exceptions()
        self.assertTrue(validation.is_valid(), msg='{} != []'.format(exns))

setattr(Test, 'test_prefix_v2_full', test_prefix_v2_full)
