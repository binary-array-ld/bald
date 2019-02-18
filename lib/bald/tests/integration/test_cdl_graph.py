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
            cdlname = 'array_reference.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, cache=self.acache)

            html = root_container.viewgraph()
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.html_path, 'array_reference.html'), 'w') as sf:
                    sf.write(html)
            with open(os.path.join(self.html_path, 'array_reference.html'), 'r') as sf:
                expected_html = sf.read()
            self.assertStringEqual(expected_html, html)

    def test_multi_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'multi_array_reference.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'file://CDL/{}'.format(cdlname)
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, cache=self.acache)

            html = root_container.viewgraph()
            if os.environ.get('bald_update_results') is not None:
                with open(os.path.join(self.html_path, 'multi_array_reference.html'), 'w') as sf:
                    sf.write(html)
            with open(os.path.join(self.html_path, 'multi_array_reference.html'), 'r') as sf:
                expected_html = sf.read()
            self.assertStringEqual(expected_html, html)
