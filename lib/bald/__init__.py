import contextlib
import re

import h5py
import netCDF4
import requests

import bald.validation as bv


class HttpCache(object):
    """
    Requests cache.
    """
    def __init__(self):
        self.cache = {}

    def is_http_uri(self, item):
        return item.startswith('http://') or item.startswith('https://')

    def __getitem__(self, item):

        if not self.is_http_uri(item):
            raise ValueError('{} is not a HTTP URI.'.format(item))
        if item not in self.cache:
            headers = {'Accept': 'text/turtle'}
            self.cache[item] = requests.get(item, headers=headers)

        return self.cache[item]

    def check_uri(self, uri):
        result = False
        if self[uri].status_code == 200:
            result = True
        return result


class Subject(object):
    def __init__(self, attrs=None, prefixes=None, aliases=None):
        """
        A subject of metadata statements.

        attrs: an dictionary of key value pair attributes
        """
        if attrs is None:
            attrs = {}
        if prefixes is None:
            prefixes = {}
        if aliases is None:
            aliases = {}
        self.attrs = attrs
        self.aliases = aliases
        self._prefixes = prefixes
        self._prefix_suffix = re.compile('(^(?:(?!__).)*)__((?!.*__).*$)')
        _http_p = 'http[s]?://.*'
        self._http_uri = re.compile('{}'.format(_http_p))
        self._http_uri_prefix = re.compile('{}/|#'.format(_http_p))

    def prefixes(self):
        prefixes = {}
        for key, value in self._prefixes.iteritems():
            if key.endswith('__') and self._http_uri_prefix.match(value):
                pref = key.rstrip('__')
                if pref in prefixes:
                    raise ValueError('This container has conflicting prefix'
                                     ' definitions.')
                prefixes[pref] = value
        return prefixes

    def unpack_uri(self, astring):
        result = astring
        if self._prefix_suffix.match(astring):
            prefix, suffix = self._prefix_suffix.match(astring).groups()
            if prefix in self.prefixes():
                if self._http_uri.match(self.prefixes()[prefix]):
                    result = astring.replace('{}__'.format(prefix),
                                             self.prefixes()[prefix])
        elif astring in self.aliases:
            result = self.aliases[astring]
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


@contextlib.contextmanager
def load(afilepath):
    if afilepath.endswith('.hdf'):
        loader = h5py.File
    elif afilepath.endswith('.nc'):
        loader = netCDF4.Dataset
    else:
        raise ValueError('filepath suffix not supported')
    try:
        f = loader(afilepath, "r")
        yield f
    finally:
        f.close()


def validate_netcdf(afilepath):
    """
    Validate a file with respect to binarry-array-linked-data.
    Returns a :class:`bald.validation.Validation`
    """

    with load(afilepath) as fhandle:
        sval = bv.StoredValidation()
        prefix_group = fhandle[fhandle.bald__isPrefixedBy] if hasattr(fhandle, 'bald__isPrefixedBy') else {}
        prefixes = {}
        if prefix_group:
            prefixes = dict([(prefix, getattr(prefix_group, prefix)) for prefix in prefix_group.ncattrs()])
        else:
            for k in fhandle.ncattrs():
                if k.endswith('__'):
                    prefixes[k] = getattr(fhandle, k)            
        attrs = {}
        for k in fhandle.ncattrs():
            attrs[k] = getattr(fhandle, k)
        root_container = Subject(attrs, prefixes=prefixes)
        root_val = bv.ContainerValidation(subject=root_container,
                                          fhandle=fhandle)
        sval.stored_exceptions += root_val.exceptions()
        for name in fhandle.variables:
            sattrs = fhandle.__dict__.copy()
            sattrs.update(fhandle.variables[name].__dict__.copy())
            var = Subject(sattrs, prefixes=prefixes)
            var_val = bv.ArrayValidation(name, fhandle.variables[name], fhandle=fhandle,
                                         subject=var)
            sval.stored_exceptions += var_val.exceptions()
            
        return sval


def validate_hdf5(afilepath):
    """
    Validate a file with respect ot binarry-array-linked-data.
    Returns a :class:`bald.validation.Validation`
    """

    with load(afilepath) as fhandle:
        sval = bv.StoredValidation()
        cache = {}
        prefix_group = fhandle.attrs.get('bald__isPrefixedBy')
        prefixes = {}
        if prefix_group:
            prefixes = fhandle[prefix_group].attrs
        alias_group = fhandle.attrs.get('bald__isAliasedBy')
        aliases = {}
        if alias_group:
            aliases = dict(fhandle[alias_group].attrs.iteritems())
        root_container = Subject(fhandle.attrs, prefixes=prefixes, aliases=aliases)
        root_val = bv.ContainerValidation(subject=root_container,
                                          fhandle=fhandle)
        sval.stored_exceptions += root_val.exceptions()
        # iterate through the datasets
        for name, dataset in fhandle.items():
            # a dataset's attribute collection inherits from and
            # specialises it's container's attrbiute collection
            # this only helps with prefixes, afaik, hence:
            # #
            sattrs = dict(fhandle.attrs).copy()
            sattrs.update(dataset.attrs)
            dset = Subject(sattrs, prefixes, aliases)
            dset_val = bv.ArrayValidation(name, dataset, fhandle=fhandle,
                                            subject=dset)
            sval.stored_exceptions += dset_val.exceptions()

        return sval
