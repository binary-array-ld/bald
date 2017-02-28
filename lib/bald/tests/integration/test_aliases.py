import unittest

import h5py
import numpy as np

import bald
from bald.tests import BaldTestCase

def _fattrs(f):
    f.attrs['rdf__type'] = 'bald__Container'
    group_pref = f.create_group('prefix_list')
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
            group_alias = f.create_group('bald__alias_list')
            f.attrs['bald__isAliasedBy'] = group_alias.ref
            group_alias.attrs['skosPrefLabel'] = 'http://www.w3.org/2004/02/skos/core#prefLabel'
            dsetp = f.create_dataset("parent_dataset", (11, 17), dtype='i')
            dsetp.attrs['skosPrefLabel'] = 'alabel'
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            self.assertTrue(validation.is_valid(), msg='{}  != []'.format(exns))

    def test_invalid_uri(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f.attrs['bald__turtle'] = 'bald__walnut'
            group_alias = f.create_group('bald__alias_list')
            f.attrs['bald__isAliasedBy'] = group_alias.ref            
            group_alias.attrs['skosPrefLabel'] = 'http://www.w3.org/2004/02/skos/core#notThisPrefLabel'
            dsetp = f.create_dataset("parent_dataset", (11, 17), dtype='i')
            dsetp.attrs['skosPrefLabel'] = 'alabel'
            f.close()
            validation = bald.validate_hdf5(tfile)
            exns = validation.exceptions()
            expected = ['http://binary-array-ld.net/latest/turtle is not resolving as a resource (404).',
                        'http://binary-array-ld.net/latest/walnut is not resolving as a resource (404).']
            self.assertTrue((not validation.is_valid()) and exns == expected,
                             msg='{}  != {}'.format(exns, expected))


if __name__ == '__main__':
    unittest.main()
