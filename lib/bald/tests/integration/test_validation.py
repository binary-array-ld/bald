import unittest

import h5py
import numpy as np

import bald
from bald.tests import BaldTestCase

def _fattrs(f):
    f.attrs['rdf__type'] = 'bald__Container'
    group_pref = f.create_group('bald_prefix_list')
    group_pref.attrs['bald__'] = 'https://www.opengis.net/def/binary-array-ld/'
    group_pref.attrs['rdf__'] = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    f.attrs['bald__isPrefixedBy'] = group_pref.ref
    return f

def _create_source_target(f, pshape, cshape):
    dsetp = f.create_dataset("source_dataset", pshape, dtype='i')
    dsetc = f.create_dataset("target_dataset", cshape, dtype='i')
    dsetp.attrs['rdf__type'] = 'bald__Array'
    dsetp.attrs['bald__references'] = dsetc.ref
    dsetc.attrs['rdf__type'] = 'bald__Array'
    dsetc.attrs['rdf__type'] = 'bald__Reference'
    # dsetc.attrs['bald__array'] = dsetc.ref
    return f


class Test(BaldTestCase):
        
    def test_valid_uri(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_source_target(f, (11, 17), (11, 17))
            f.close()
            validation = bald.validate_hdf5(tfile, cache=self.acache)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exns))

    def test_invalid_uri(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_source_target(f, (11, 17), (11, 17))
            f.attrs['bald__turtle'] = 'bald__walnut'
            f.close()
            validation = bald.validate_hdf5(tfile, cache=self.acache,
                                            uris_resolve=True)
            exns = validation.exceptions()
            expected = ['https://www.opengis.net/def/binary-array-ld/turtle is not resolving as a resource (404).',
                        'https://www.opengis.net/def/binary-array-ld/walnut is not resolving as a resource (404).']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))

class TestArrayReference(BaldTestCase):
    def test_match(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_source_target(f, (11, 17), (11, 17))
            f.close()
            validation = bald.validate_hdf5(tfile, cache=self.acache)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exns))

    def test_mismatch_zeroth(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_source_target(f, (11, 17), (11, 13))
            f.close()
            fname = ('file:///tests/integration/test_validation/Test/'
                     'test_mismatch_zeroth.hdf')
            validation = bald.validate_hdf5(tfile, baseuri=fname, cache=self.acache)
            exns = validation.exceptions()
            expected = ['file:///tests/integration/test_validation/Test/'
                        'test_mismatch_zeroth.hdf/source_dataset declares a '
                        'target of file:///tests/integration/test_validation/'
                        'Test/test_mismatch_zeroth.hdf/target_dataset but the '
                        'arrays do not conform to the bald array reference '
                        'rules']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))

    def test_mismatch_oneth(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_source_target(f, (11, 17), (13, 17))
            f.close()
            fname = ('file:///tests/integration/test_validation/Test/'
                     'test_mismatch_oneth.hdf')
            validation = bald.validate_hdf5(tfile, baseuri=fname, cache=self.acache)
            exns = validation.exceptions()
            expected = ['file:///tests/integration/test_validation/Test/'
                        'test_mismatch_oneth.hdf/source_dataset declares a '
                        'target of file:///tests/integration/test_validation/'
                        'Test/test_mismatch_oneth.hdf/target_dataset but the'
                        ' arrays do not conform to the bald array reference '
                        'rules']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))

    def test_match_plead_dim(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            # source has leading dimension wrt target
            f = _create_source_target(f, (4, 13, 17), (13, 17))
            f.close()
            validation = bald.validate_hdf5(tfile, cache=self.acache)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exns))

    def test_match_clead_dim(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            # target has leading dimension wrt source
            f = _create_source_target(f, (13, 17), (7, 13, 17))
            f.close()
            validation = bald.validate_hdf5(tfile, cache=self.acache)
            exs = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exs))

    def test_mismatch_pdisjc_lead_dim(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            # target and source have disjoint leading dimensions
            f = _create_source_target(f, (4, 13, 17), (7, 13, 17))
            
            f.close()
            fname = ('file:///tests/integration/test_validation/Test/'
                     'test_mismatch_pdisjc_lead_dim.hdf')
            validation = bald.validate_hdf5(tfile, baseuri=fname, cache=self.acache)

            exns = validation.exceptions()
            expected = ['file:///tests/integration/test_validation/Test/'
                        'test_mismatch_pdisjc_lead_dim.hdf/source_dataset '
                        'declares a target of file:///tests/integration/'
                        'test_validation/Test/test_mismatch_pdisjc_lead_dim'
                        '.hdf/target_dataset but the arrays do not conform to'
                        ' the bald array reference rules']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))

    def test_mismatch_pdisjc_trail_dim(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            # target and source have disjoint trailing dimensions
            f = _create_source_target(f, (13, 17, 2), (13, 17, 9))
            f.close()
            fname = ('file:///tests/integration/test_validation/Test/'
                     'test_mismatch_pdisjc_trail_dim.hdf')
            validation = bald.validate_hdf5(tfile, baseuri=fname, cache=self.acache)

            exns = validation.exceptions()
            expected = ['file:///tests/integration/test_validation/Test/'
                        'test_mismatch_pdisjc_trail_dim.hdf/source_dataset'
                        ' declares a target of file:///tests/integration/'
                        'test_validation/Test/test_mismatch_pdisjc_trail_dim'
                        '.hdf/target_dataset but the arrays do not conform to '
                        'the bald array reference rules']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))


if __name__ == '__main__':
    unittest.main()
