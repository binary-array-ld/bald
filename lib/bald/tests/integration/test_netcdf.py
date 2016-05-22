import unittest

import h5py
import netCDF4
import numpy as np

import bald
from bald.tests import BaldTestCase

def _fattrs(f):
    f.bald__ = 'http://binary-array-ld.net/experimental/'
    f.rdf__ = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    f.rdf__type =  'bald__Container'
    return f


class Test(BaldTestCase):
        
    def test_valid_uri(self):
        with self.temp_filename('.nc') as tfile:
            f = netCDF4.Dataset(tfile, "w", format="NETCDF4")

            f = _fattrs(f)
            f.close()
            validation = bald.validate_netcdf(tfile)
            self.assertTrue(validation.is_valid())

    def test_invalid_uri(self):
        with self.temp_filename('.nc') as tfile:
            f = netCDF4.Dataset(tfile, "w", format="NETCDF4")

            f = _fattrs(f)
            setattr(f, 'bald__turtle', 'bald__walnut')
            f.close()
            validation = bald.validate_netcdf(tfile)
            self.assertFalse(validation.is_valid())


if __name__ == '__main__':
    unittest.main()




