import unittest

import h5py
import numpy as np

import bald
from bald.tests import BaldTestCase

def _fattrs(f):
    f.attrs['rdf__type'] = 'bald__Container'
    group_pref = f.create_group('bald_prefix_list')
    group_pref.attrs['bald__'] = 'http://binary-array-ld.net/latest/'
    group_pref.attrs['rdf__'] = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    f.attrs['bald__isPrefixedBy'] = group_pref.ref
    return f

def _create_parent_child(f, pshape, cshape):
    dsetp = f.create_dataset("parent_dataset", pshape, dtype='i')
    dsetc = f.create_dataset("child_dataset", cshape, dtype='i')
    dsetp.attrs['rdf__type'] = 'bald__Array'
    dsetp.attrs['bald__references'] = dsetc.ref
    dsetc.attrs['rdf__type'] = 'bald__Array'
    dsetc.attrs['rdf__type'] = 'bald__Reference'
    dsetc.attrs['bald__array'] = dsetc.ref
    return f


class Test(BaldTestCase):
        
    def test_valid_uri(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 17))
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exns))

    def test_invalid_uri(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 17))
            f.attrs['bald__turtle'] = 'bald__walnut'
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            expected = ['http://binary-array-ld.net/latest/turtle is not resolving as a resource (404).',
                        'http://binary-array-ld.net/latest/walnut is not resolving as a resource (404).']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))

class TestArrayReference(BaldTestCase):
    def test_match(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 17))
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exns))

    def test_mismatch_zeroth(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (11, 13))
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            expected = ['p declares a child of c but the arrays do not conform to the bald array reference rules']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))

    def test_mismatch_oneth(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, (11, 17), (13, 17))
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            expected = ['p declares a child of c but the arrays do not conform to the bald array reference rules']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))

    def test_match_plead_dim(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            # parent has leading dimension wrt child
            f = _create_parent_child(f, (4, 13, 17), (13, 17))
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exns))

    def test_match_clead_dim(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            # child has leading dimension wrt parent
            f = _create_parent_child(f, (13, 17), (7, 13, 17))
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exns))

    def test_mismatch_pdisjc_lead_dim(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            # child and parent have disjoint leading dimensions
            f = _create_parent_child(f, (4, 13, 17), (7, 13, 17))
            
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            expected = ['p declares a child of c but the arrays do not conform to the bald array reference rules']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))

    def test_mismatch_pdisjc_trail_dim(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            # child and parent have disjoint trailing dimensions
            f = _create_parent_child(f, (13, 17, 2), (13, 17, 9))
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            expected = ['p declares a child of c but the arrays do not conform to the bald array reference rules']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))


if __name__ == '__main__':
    unittest.main()
