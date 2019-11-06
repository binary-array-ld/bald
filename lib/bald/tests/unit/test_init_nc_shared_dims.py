from collections import OrderedDict
import unittest

import bald

class netcdfVarMin(object):
    def __init__(self, dim_tuple, shape_tuple):
        self.dimensions = dim_tuple
        self.shape = shape_tuple
        if len(self.dimensions) != len(self.shape):
            raise ValueError('dim_tuple and shape_tuple must be tuples'
                             ' of the same length')

class Test(unittest.TestCase):
    #def setup(self)
    def test_same_two(self):
        source_var = netcdfVarMin(('a', 'b'), (3, 5))
        target_var = netcdfVarMin(('a', 'b'), (3, 5))
        expected = OrderedDict((('a', 3), ('b', 5)))
        result = bald.netcdf_shared_dimensions(source_var, target_var)
        with self.subTest():
            self.assertDictEqual(result.get('sourceReshape', dict()), expected)
        with self.subTest():
            self.assertDictEqual(result.get('targetReshape', dict()), expected)

    def test_target_subset_last(self):
        source_var = netcdfVarMin(('a', 'b', 'c'), (3, 5, 7))
        target_var = netcdfVarMin(('b', 'c'), (5, 7))
        expected_source = OrderedDict((('a', 3), ('b', 5), ('c', 7)))
        expected_target = OrderedDict((('a', 1), ('b', 5), ('c', 7)))
        result = bald.netcdf_shared_dimensions(source_var, target_var)
        with self.subTest():
            self.assertDictEqual(result.get('sourceReshape', dict()),
                                 expected_source)
        with self.subTest():
            self.assertDictEqual(result.get('targetReshape', dict()),
                                 expected_target)


    def test_target_subset_first(self):
        source_var = netcdfVarMin(('a', 'b', 'c'), (3, 5, 7))
        target_var = netcdfVarMin(('a', 'b'), (3, 5))
        expected_source = OrderedDict((('a', 3), ('b', 5), ('c', 7)))
        expected_target = OrderedDict((('a', 3), ('b', 5), ('c', 1)))
        result = bald.netcdf_shared_dimensions(source_var, target_var)
        with self.subTest():
            self.assertDictEqual(result.get('sourceReshape', dict()),
                                 expected_source)
        with self.subTest():
            self.assertDictEqual(result.get('targetReshape', dict()),
                                 expected_target)


    def test_disjoint_misalign(self):
        source_var = netcdfVarMin(('a', 'b', 'c'), (3, 5, 7))
        target_var = netcdfVarMin(('b', 'c', 'd'), (5, 7, 9))
        expected_source = OrderedDict((('a', 3), ('b', 5), ('c', 7), ('d', 1)))
        expected_target = OrderedDict((('a', 1), ('b', 5), ('c', 7), ('d', 9)))
        result = bald.netcdf_shared_dimensions(source_var, target_var)
        with self.subTest():
            self.assertDictEqual(result.get('sourceReshape', dict()),
                                 expected_source)
        with self.subTest():
            self.assertDictEqual(result.get('targetReshape', dict()),
                                 expected_target)

    def test_disjoint_misalign_invert(self):
        source_var = netcdfVarMin(('b', 'c', 'd'), (5, 7, 9))
        target_var = netcdfVarMin(('a', 'b', 'c'), (3, 5, 7))
        expected_source = OrderedDict((('a', 1), ('b', 5), ('c', 7), ('d', 9)))
        expected_target = OrderedDict((('a', 3), ('b', 5), ('c', 7), ('d', 1)))
        result = bald.netcdf_shared_dimensions(source_var, target_var)
        with self.subTest():
            self.assertDictEqual(result.get('sourceReshape', dict()),
                                 expected_source)
        with self.subTest():
            self.assertDictEqual(result.get('targetReshape', dict()),
                                 expected_target)

    def test_disjoint_align_interleave(self):
        source_var = netcdfVarMin(('a', 'c', 'd', 'e', 'f'), (3, 7, 9, 11, 13))
        target_var = netcdfVarMin(('a', 'b', 'c', 'f'), (3, 5, 7, 13))
        expected_source = OrderedDict((('a', 3), ('b', 1), ('c', 7), ('d', 9),
                                       ('e', 11), ('f', 13)))
        expected_target = OrderedDict((('a', 3), ('b', 5), ('c', 7), ('d', 1),
                                       ('e', 1), ('f', 13)))
        result = bald.netcdf_shared_dimensions(source_var, target_var)
        with self.subTest():
            self.assertDictEqual(result.get('sourceReshape', dict()),
                                 expected_source)
        with self.subTest():
            self.assertDictEqual(result.get('targetReshape', dict()),
                                 expected_target)

    def test_disjoint_misalign_interleave(self):
        source_var = netcdfVarMin(('b', 'c', 'd', 'e', 'f'), (5, 7, 9, 11, 13))
        target_var = netcdfVarMin(('a', 'b', 'c', 'f'), (3, 5, 7, 13))
        expected_source = OrderedDict((('a', 1), ('b', 5), ('c', 7), ('d', 9),
                                       ('e', 11), ('f', 13)))
        expected_target = OrderedDict((('a', 3), ('b', 5), ('c', 7), ('d', 1),
                                       ('e', 1), ('f', 13)))
        result = bald.netcdf_shared_dimensions(source_var, target_var)
        with self.subTest():
            self.assertDictEqual(result.get('sourceReshape', dict()),
                                 expected_source)
        with self.subTest():
            self.assertDictEqual(result.get('targetReshape', dict()),
                                 expected_target)

