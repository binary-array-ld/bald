import unittest

import h5py
import numpy as np

from bald.tests import BaldTestCase
import bald

class TestHttpCache(unittest.TestCase):
    def setUp(self):
        self.cache = bald.HttpCache()

    def test_check_uri_200(self):
        auri = 'http://binary-array-ld.net/experimental'
        self.assertTrue(self.cache.check_uri(auri))

    def test_check_uri_404(self):
        notauri = 'http://binary-array-ld.net/experimentalish'
        self.assertFalse(self.cache.check_uri(notauri))


if __name__ == '__main__':
    unittest.main()
