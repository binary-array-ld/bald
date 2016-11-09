import contextlib
import re

import h5py
import netCDF4
import requests

import bald.validation as bv

__version__ = '0.2'

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
    def __init__(self, attrs=None, prefixes=None, aliases=None,
                 rdftype='bald__Subject'):
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
        if 'rdf__type' not in attrs:
            attrs['rdf__type'] = rdftype
        elif rdftype not in attrs['rdf__type']:
            if isinstance(attrs['rdf__type'], list):
                attrs['rdf__type'].append(rdftype)
            elif isinstance(attrs['rdf__type'], set):
                attrs['rdf__type'].add(rdftype)
            else:
                attrs['rdf__type'] = set((attrs['rdf__type'], rdftype))

        self.aliases = aliases
        self._prefixes = prefixes
        self._prefix_suffix = re.compile('(^(?:(?!__).)*)__((?!.*__).*$)')
        _http_p = 'http[s]?://.*'
        self._http_uri = re.compile('{}'.format(_http_p))
        self._http_uri_prefix = re.compile('{}/|#'.format(_http_p))

    def __str__(self):
        return '{}: {}'.format(type(self), self.attrs)

    def __repr__(self):
        return str(self)

    def __getattr__(self, attr):
        if attr not in self.attrs:
            msg = '{} object has no attribute {}'.format(type(self), attr)
            raise AttributeError(msg)
        return self.attrs[attr]

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

    def graph(self):
        graph = rdflib.Graph()
        
        return graph

class Array(Subject):
    def __init__(self, attrs=None, prefixes=None, aliases=None,
                 shape=None):
        self.shape = shape
        rdftype = 'bald__Array'
        super(Array, self).__init__(attrs, prefixes, aliases, rdftype)

    @property
    def array_references(self):
        return self.attrs.get('bald__references', [])
        #return []

class Container(Subject):
    def __init__(self, attrs=None, prefixes=None, aliases=None,
                 shape=None):
        rdftype = 'bald__Container'
        super(Container, self).__init__(attrs, prefixes, aliases, rdftype)

    
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

def load_netcdf(afilepath):
    """
    Validate a file with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`
    """

    with load(afilepath) as fhandle:
        prefix_group = (fhandle[fhandle.bald__isPrefixedBy] if
                        hasattr(fhandle, 'bald__isPrefixedBy') else {})
        prefixes = {}
        if prefix_group:
            prefixes = (dict([(prefix, getattr(prefix_group, prefix)) for
                              prefix in prefix_group.ncattrs()]))
        else:
            for k in fhandle.ncattrs():
                if k.endswith('__'):
                    prefixes[k] = getattr(fhandle, k)
        alias_group = (fhandle[fhandle.bald__isAliasedBy]
                       if hasattr(fhandle, 'bald__isAliasedBy') else {})
        aliases = {}
        if alias_group:
            aliases = (dict([(alias, getattr(alias_group, alias))
                             for alias in alias_group.ncattrs()]))

        attrs = {}
        for k in fhandle.ncattrs():
            attrs[k] = getattr(fhandle, k)
        # It would be nice to use the URI of the file if it is known. 
        attrs['@id'] = 'root'
        root_container = Container(attrs, prefixes=prefixes,
                                   aliases=aliases)
        root_container.attrs['bald__contains'] = []

        for name in fhandle.variables:

            sattrs = fhandle.variables[name].__dict__.copy()
            sattrs['@id'] = '/{}'.format(name)

            if 'bald__references' in fhandle.variables[name].ncattrs():
                child_dset = fhandle.variables[fhandle.variables[name].bald__references]
                cattrs = child_dset.__dict__.copy()
                cattrs['@id'] = '/{}'.format(child_dset.name)
                carray = Array(cattrs, prefixes, aliases, child_dset.shape)
                sattrs['bald__references'] = [carray]
            
            var = Array(sattrs, prefixes=prefixes, aliases=aliases,
                        shape=fhandle.variables[name].shape)
            root_container.attrs['bald__contains'].append(var)
            

    return root_container


def validate_netcdf(afilepath):
    """
    Validate a file with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`

    """
    root_container = load_netcdf(afilepath)
    return validate(root_container)


def validate_hdf5(afilepath):
    """
    Validate a file with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`

    """
    root_container = load_hdf5(afilepath)
    return validate(root_container)

def validate(root_container):
    """
    Validate a Container with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`

    """
    sval = bv.StoredValidation()

    root_val = bv.ContainerValidation(subject=root_container)
    sval.stored_exceptions += root_val.exceptions()
    for subject in root_container.attrs.get('bald__contains', []):
        
        # a dataset's attribute collection inherits from and
        # specialises it's container's attrbiute collection
        # this only helps with prefixes, afaik, hence:
        # #
        array_val = bv.ArrayValidation(subject)
        sval.stored_exceptions += array_val.exceptions()

    return sval

def load_hdf5(afilepath):
    with load(afilepath) as fhandle:
        # unused?
        cache = {}
        prefix_group = fhandle.attrs.get('bald__isPrefixedBy')
        prefixes = {}
        if prefix_group:
            prefixes = dict(fhandle[prefix_group].attrs)
        alias_group = fhandle.attrs.get('bald__isAliasedBy')
        aliases = {}
        if alias_group:
            aliases = dict(fhandle[alias_group].attrs)
        attrs = dict(fhandle.attrs)
        attrs['@id'] = 'root'
        root_container = Container(attrs, prefixes=prefixes, aliases=aliases)

        root_container.attrs['bald__contains'] = []

        # iterate through the datasets
        for name, dataset in fhandle.items():
            if hasattr(dataset, 'shape'):
                sattrs = dict(dataset.attrs)
                sattrs['@id'] = dataset.name
                ref = sattrs.get('bald__references', '')
                if ref:
                    ref_dset = fhandle[ref]
                    child_dset = fhandle[ref_dset.attrs.get('bald__array',
                                                            None)]
                    if child_dset:
                        cattrs = dict(child_dset.attrs)
                        cattrs['@id'] = child_dset.name
                        carray = Array(cattrs, prefixes, aliases,
                                       child_dset.shape)
                        sattrs['bald__references'] = [carray]
                dset = Array(sattrs, prefixes, aliases, dataset.shape)
                root_container.attrs['bald__contains'].append(dset)
            
    return root_container

    
