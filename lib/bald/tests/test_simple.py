import unittest

import h5py
import numpy as np

from bald.tests import BaldTestCase


class Test(BaldTestCase):
    def setUp(self):
        self.this = 'this'

    def test_this(self):
        self.assertTrue(self.this, 'this')

    def test_make_file(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            dset = f.create_dataset("mydataset", (100,), dtype='i')

    def test_make_load_file(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            dset = f.create_dataset("mydataset", (100,), dtype='i')
            dset.attrs['bald__'] = 'http://binary_array_ld.net/experimental'
            f.close()
            newf = h5py.File(tfile, "r")
            nset = newf.get('mydataset')
            self.assertEqual(nset.shape, (100,))
            self.assertEqual(nset.dtype, 'int32')
            self.assertEqual(nset.attrs.get('bald__'),
                             'http://binary_array_ld.net/experimental')


if __name__ == '__main__':
    unittest.main()
