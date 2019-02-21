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


# Generate 1 test case for each file in the CDL folder
for cdl_file in glob.glob(os.path.join(os.path.dirname(__file__), 'CDL', '*.cdl')):
    file_id = os.path.basename(cdl_file).split('.cdl')[0]

    def make_a_test(cdlfile):
        def atest(self):
            with self.temp_filename('.nc') as tfile:
                subprocess.check_call(['ncgen', '-o', tfile, cdlfile])
                validation = bald.validate_netcdf(tfile, cache=self.acache)
                exns = validation.exceptions()
                self.assertTrue(validation.is_valid(), msg='{} != []'.format(exns))
        return atest
    setattr(Test, 'test_{}'.format(file_id), make_a_test(cdl_file))
