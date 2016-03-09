import unittest

import h5py
import numpy as np

from bald.tests import BaldTestCase

def _fattrs(f):
    f.attrs['bald_._'] = 'http://binary_array_ld.net/experimental'
    f.attrs['bald_._type'] = 'bald_._Container'
    return f

def _create_parent_child(f, pshape, cshape):
    dsetp = f.create_dataset("parent_dataset", pshape, dtype='i')
    dsetc = f.create_dataset("child_dataset", cshape, dtype='i')
    dsetp.attrs['bald_._type'] = 'bald_._Dataset'
    dsetp.attrs['bald_._reference'] = dsetc.ref
    dsetc.attrs['bald_._type'] = 'bald_._Dataset'
    return f


class TestArrayReference(BaldTestCase):
    def test_match_array_reference(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 17))
            f.close()


if __name__ == '__main__':
    unittest.main()
