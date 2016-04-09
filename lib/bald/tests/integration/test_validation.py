import unittest

import h5py
import numpy as np

import bald
from bald.tests import BaldTestCase

def _fattrs(f):
    f.attrs['bald_._'] = 'http://binary-array-ld.net/experimental/'
    f.attrs['bald_._type'] = 'bald_._Container'
    return f

def _create_parent_child(f, pshape, cshape):
    dsetp = f.create_dataset("parent_dataset", pshape, dtype='i')
    dsetc = f.create_dataset("child_dataset", cshape, dtype='i')
    dsetp.attrs['bald_._type'] = 'bald_._Dataset'
    dsetp.attrs['bald_._reference'] = dsetc.ref
    dsetc.attrs['bald_._type'] = 'bald_._Dataset'
    return f


class Test(BaldTestCase):
        
    def test_valid_uri(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 17))
            f.close()
            self.assertTrue(bald.validate_hdf5(tfile))

    def test_invalid_uri(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 17))
            f.attrs['bald_._turtle'] = 'bald_._walnut'
            f.close()
            self.assertFalse(bald.validate_hdf5(tfile))

class TestArrayReference(BaldTestCase):
    def test_match_array_reference(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 17))
            f.close()
            self.assertTrue(bald.validate_hdf5(tfile))

    def test_misatch_zeroth_array_reference(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 13))
            f.close()
            self.assertFalse(bald.validate_hdf5(tfile))

    def test_misatch_oneth_array_reference(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (13, 17))
            f.close()
            self.assertFalse(bald.validate_hdf5(tfile))


if __name__ == '__main__':
    unittest.main()
