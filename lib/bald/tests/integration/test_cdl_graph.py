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
        self.html_path = os.path.join(os.path.dirname(__file__), 'HTML')
        
    def test_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'array_reference.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            root_container = bald.load_netcdf(tfile)
            html = root_container.viewgraph()
            # with open(os.path.join(self.html_path, 'array_reference.html'), 'w') as sf:
            #     sf.write(html)
            with open(os.path.join(self.html_path, 'array_reference.html'), 'r') as sf:
                expected_html = sf.read()
            self.assertStringEqual(expected_html, html)

    def test_multi_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'multi_array_reference.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            root_container = bald.load_netcdf(tfile)
            html = root_container.viewgraph()
            # with open(os.path.join(self.html_path, 'multi_array_reference.html'), 'w') as sf:
            #     sf.write(html)
            with open(os.path.join(self.html_path, 'multi_array_reference.html'), 'r') as sf:
                expected_html = sf.read()
            self.assertStringEqual(expected_html, html)
