import unittest

import h5py
import numpy as np

from bald.tests import BaldTestCase

def _fattrs(f):
    f.attrs['bald__'] = 'http://binary_array_ld.net/experimental'
    f.attrs['bald__type'] = 'bald__Container'
    return f

def _create_parent_child(f, pshape, cshape):
    dsetp = f.create_dataset("parent_dataset", pshape, dtype='i')
    dsetc = f.create_dataset("child_dataset", cshape, dtype='i')
    dsetp.attrs['bald__type'] = 'bald__Dataset'
    dsetp.attrs['bald__reference'] = dsetc.ref
    dsetc.attrs['bald__type'] = 'bald__Dataset'
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
