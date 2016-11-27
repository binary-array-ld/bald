import os
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
    group_pref.attrs['skos__'] = 'http://www.w3.org/2004/02/skos/core#'
    f.attrs['bald__isPrefixedBy'] = group_pref.ref
    return f

def _create_parent_child(container, pname, pshape, cname, cshape):
    dsetp = container.create_dataset(pname, pshape, dtype='i')
    dsetc = container.create_dataset(cname, cshape, dtype='i')
    dsetp.attrs['rdf__type'] = 'bald__Array'
    dsetp.attrs['bald__references'] = dsetc.ref
    dsetc.attrs['rdf__type'] = 'bald__Array'
    dsetc.attrs['rdf__type'] = 'bald__Reference'
    dsetc.attrs['bald__array'] = dsetc.ref
    return container


class TestHDFGraph(BaldTestCase):
    def setUp(self):
        self.html_path = os.path.join(os.path.dirname(__file__), 'HTML')

    def test_match(self):
        with self.temp_filename('.hdf') as tfile:
            f = h5py.File(tfile, "w")
            f = _fattrs(f)
            f = _create_parent_child(f, 'data', (11, 17), 'alocation', (11, 17))
            group_d = f.create_group('discovery')
            group_s = group_d.create_group('source')
            group_r = f.create_group('referencing')
            _create_parent_child(group_d, 'apair', (2,), 'anotherpair', (2,))
            inst = group_s.create_dataset('institution', ())
            inst.attrs['skos__prefLabel'] = 'a quality establishment'
            sref = group_r.create_dataset('locref', ())
            sref.attrs['skos__prefLabel'] = 'for locational purposes'
            sref2 = group_r.create_dataset('locref2', ())
            sref2.attrs['skos__prefLabel'] = 'for more locational purposes'
            f['alocation'].attrs['bald__references'] = np.array([sref.ref, sref2.ref],
                                                               dtype=h5py.special_dtype(ref=h5py.Reference))
            f.close()
            root_container = bald.load_hdf5(tfile)
        html = root_container.viewgraph()
        with open(os.path.join(self.html_path, 'hdf_container_nest.html'), 'w') as sf:
            sf.write(html)


if __name__ == '__main__':
    unittest.main()
