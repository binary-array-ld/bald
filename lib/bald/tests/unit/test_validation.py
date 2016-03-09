import unittest

import h5py
import numpy as np

from bald.tests import BaldTestCase
from bald import validation

class Test(unittest.TestCase):
    def test_check_uri_200(self):
        auri = 'http://binary-array-ld.net/experimental'
        self.assertTrue(validation.check_uri(auri))

    def test_check_uri_404(self):
        notauri = 'http://binary-array-ld.net/experimentalish'
        self.assertFalse(validation.check_uri(notauri))


if __name__ == '__main__':
    unittest.main()
