import contextlib
import difflib
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
    def assertStringEqual(self, first, second, msg=None):
        assertion_func = self._getAssertEqualityFunc(first, second)
        if msg is None:
            diff = difflib.ndiff(first.splitlines(1), second.splitlines(1))
            # diff = ['{0:03}'.format(i) + ' ' + line for i, line in enumerate(diff)
            #         if line.startswith('+') or line.startswith('-')]
            linecount = 0
            dlines = [' diff:\n']
            for line in diff:
                if line.startswith(' ') or line.startswith('-'):
                    linecount += 1
                if line.startswith('+') or line.startswith('-'):
                    dlines.append('{0:03} {1}'.format(linecount, line))
            msg = ''.join(dlines)

        assertion_func(first, second, msg=msg)
