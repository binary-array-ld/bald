import unittest

import h5py
import netCDF4
import numpy as np

import bald
from bald.tests import BaldTestCase

def _fattrs(f):
    f.bald__ = 'https://www.opengis.net/def/binary-array-ld/'
    f.rdf__ = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    f.rdf__type =  'bald__Container'
    return f

def _create_parent_child(f, pshape, cshape):
    for i, pdimsize in enumerate(pshape):
        f.createDimension("pdim{}".format(str(i)), pdimsize)
    for i, cdimsize in enumerate(cshape):
        f.createDimension("cdim{}".format(str(i)), cdimsize)
    varp = f.createVariable("source_variable", 'i4', tuple(["pdim{}".format(str(i)) for i, _ in enumerate(pshape)]))
    varc = f.createVariable("target_variable", 'i4', tuple(["cdim{}".format(str(i)) for i, _ in enumerate(cshape)]))
    varp.rdf__type = 'bald__Array'
    varp.bald__references = "target_variable"
    varc.rdf__type = 'bald__Array'
    varc.rdf__type = 'bald__Reference'
    return f


class Test(BaldTestCase):
        
    def test_valid_uri(self):
        with self.temp_filename('.nc') as tfile:
            f = netCDF4.Dataset(tfile, "w", format="NETCDF4_CLASSIC")

            f = _fattrs(f)
            f.close()
            validation = bald.validate_netcdf(tfile, cache=self.acache)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exns))


    def test_invalid_uri(self):
        with self.temp_filename('.nc') as tfile:
            f = netCDF4.Dataset(tfile, "w", format="NETCDF4_CLASSIC")

            f = _fattrs(f)
            setattr(f, 'bald__turtle', 'bald__walnut')
            f.close()
            validation = bald.validate_netcdf(tfile, cache=self.acache,
                                              uris_resolve=True)
            exns = validation.exceptions()

            expected =  ['https://www.opengis.net/def/binary-array-ld/ is not resolving as a resource (404).', 
                        'https://www.opengis.net/def/binary-array-ld/turtle is not resolving as a resource (404).', 
                        'https://www.opengis.net/def/binary-array-ld/walnut is not resolving as a resource (404).']

            self.assertTrue((not validation.is_valid()) and list(set((exns))) == expected,
                             msg='{}  != {}'.format(exns, expected))


class TestArrayReference(BaldTestCase):
    def test_match(self):
        with self.temp_filename('.nc') as tfile:
            f = netCDF4.Dataset(tfile, "w", format="NETCDF4_CLASSIC")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 17))
            f.close()
            validation = bald.validate_netcdf(tfile, cache=self.acache)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exns))

    def test_mismatch_zeroth(self):
        with self.temp_filename('.nc') as tfile:
            f = netCDF4.Dataset(tfile, "w", format="NETCDF4_CLASSIC")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 13))
            f.close()
            validation = bald.validate_netcdf(tfile, cache=self.acache)
            exns = validation.exceptions()
            expected = [('file://{t}/source_variable declares a target of '
                         'file://{t}/target_variable but the arrays do not '
                         'conform to the bald array reference rules'
                         '').format(t=tfile)]
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))


if __name__ == '__main__':
    unittest.main()




