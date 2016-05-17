import contextlib
import os
import tempfile
import unittest


class BaldTestCase(unittest.TestCase):
    @contextlib.contextmanager
    def temp_filename(self, suffix=''):
        temp_file = tempfile.mkstemp(suffix)
        os.close(temp_file[0])
        filename = temp_file[1]
        try:
            yield filename
        finally:
            os.remove(filename)
