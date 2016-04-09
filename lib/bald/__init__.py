import contextlib
import re

import h5py
import requests

from bald.validation import ContainerValidation, DatasetValidation


class HttpStatusCache(object):
    def __init__(self):
        self.cache = {}

    def __getitem__(self, item):

        if not item.startswith('http://') or item.startswith('https://'):
            raise ValueError('{} is not a HTTP URI.'.format(item))
        if item not in self.cache:
            headers={'Accept':'text/turtle'}
            self.cache[item] = requests.get(item, headers=headers)

        return self.cache[item]
        

    def check_uri(self, uri):
        result = False
        if self[uri].status_code == 200:
            result = True
        return result

class Subject(object):
    def __init__(self, attrs=None):
        """
        attrs: an dictionary of key value pair attributes
        """
        if attrs is None:
            attrs = []
        self.attrs = attrs
        self._prefix_suffix = re.compile('(^(?:(?!_._).)*)_._((?!.*_._).*$)')
        _http_p = 'http[s]?://.*'
        self._http_uri = re.compile('{}'.format(_http_p))
        self._http_uri_prefix = re.compile('{}/|#'.format(_http_p))


    def prefixes(self):
        prefixes = {}
        for key, value in self.attrs.iteritems():
            if key.endswith('_._') and self._http_uri_prefix.match(value):
                pref = key.rstrip('_._')
                if prefixes.has_key(pref):
                    raise ValueError('This container has conflicting prefix definitions')
                prefixes[pref] = value
        return prefixes


    def unpack_uri(self, astring):
        result = astring
        if self._prefix_suffix.match(astring):
            prefix, suffix = self._prefix_suffix.match(astring).groups()

            if self.prefixes().has_key(prefix):
                if self._http_uri.match(self.prefixes()[prefix]):
                    result = astring.replace('{}_._'.format(prefix), self.prefixes()[prefix])
        return result

@contextlib.contextmanager
def load(afilepath):
    if afilepath.endswith('.hdf'):
        loader = h5py.File
    else:
        raise ValueError('filepath suffix not supported')
    try:
        f = loader(afilepath, "r")
        yield f
    finally:
        f.close()


def validate_hdf5(afilepath):
    """
    Validate a file with respect ot binarry-array-linked-data.
    Returns a :class:`bald.validation.Validation` 
    """
    
    with load(afilepath) as fhandle:
        valid = True
        cache = {}
        root_container = Subject(fhandle.attrs)
        root_val = ContainerValidation(subject=root_container, fhandle=fhandle)
        if not root_val.is_valid():
            valid = False
        # iterate through the datasets
        for name, dataset in fhandle.items():
            # a dataset's attribute collection inherits from and specialises it's
            # container's attrbiute collection
            sattrs = dict(fhandle.attrs).copy()
            sattrs.update(dataset.attrs)
            dset = Subject(sattrs)
            dset_val = DatasetValidation(name, dataset, fhandle=fhandle, subject=dset)
            if not dset_val.is_valid():
                valid = False
        
        return valid
        
        

    
