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

    def test_array_reference(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'array_reference.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            validation = bald.validate_netcdf(tfile)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{} != []'.format(exns))

    def test_alias(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'array_alias.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            validation = bald.validate_netcdf(tfile)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{} != []'.format(exns))

    # def test_process_chain(self):
    #     with self.temp_filename('.nc') as tfile:
    #         cdl_file = os.path.join(self.cdl_path, 'ProcessChain0300.cdl')
    #         subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
    #         validation = bald.validate_netcdf(tfile)
    #         exns = validation.exceptions()
    #         self.assertTrue(validation.is_valid(), msg='{} != []'.format(exns))

    def test_ereef(self):
        with self.temp_filename('.nc') as tfile:
            cdl_file = os.path.join(self.cdl_path, 'ereefs-gbr4_ncld.cdl')
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            validation = bald.validate_netcdf(tfile)
            exns = validation.exceptions()
            exns.sort()
            expected = ['http://qudt.org/vocab/unit#Meter is not resolving as a resource (404).',
                        'p declares a child of c but the arrays do not conform to the bald array reference rules',
                        'http://qudt.org/vocab/unit#MeterPerSecond is not resolving as a resource (404).',
                        'p declares a child of c but the arrays do not conform to the bald array reference rules',
                        'http://qudt.org/vocab/unit#MeterPerSecond is not resolving as a resource (404).',
                        'p declares a child of c but the arrays do not conform to the bald array reference rules',
                        'p declares a child of c but the arrays do not conform to the bald array reference rules',
                        'http://qudt.org/vocab/unit#DegreeCelsius is not resolving as a resource (404).',
                        'p declares a child of c but the arrays do not conform to the bald array reference rules',
                        'p declares a child of c but the arrays do not conform to the bald array reference rules',
                        'p declares a child of c but the arrays do not conform to the bald array reference rules']
            expected.sort()
            self.assertTrue(not validation.is_valid() and exns == expected,
                            msg='{} \n!= \n{}'.format(exns, expected))
