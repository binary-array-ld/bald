
import numpy as np
import rdflib

import bald


def valid_array_reference(parray, carray, broadcast_shape=None):
    """
    Returns boolean.
    Validates bald array broadcasting rules between one parent array and
    one child array.

    Args:
        * parray - a numpy array: the parent of a bald array reference relation

        * carray - a numpy array: the child of a bald array reference relation

        * broadcast_shape - a string defining the ordered list of dimensions
                            and sizes for the resulting array from broadcasting
                            parry and carray;
                            e.g. (1, 1, 4, 9)
    """
    # https://github.com/SciTools/courses/blob/master/course_content/notebooks/numpy_intro.ipynb
    # https://cs231n.github.io/python-numpy-tutorial/#numpy-broadcasting
    # http://docs.scipy.org/doc/numpy/user/basics.broadcasting.html
    # http://scipy.github.io/old-wiki/pages/EricsBroadcastingDoc

    result = True
    # try numpy broadcast
    try:
        _ = np.broadcast(parray, carray)
    except ValueError:
        result = False

    return result


class Validation(object):

    def is_valid(self):
        return not self.exceptions()

    def exceptions(self):
        exceptions = []
        return exceptions


class StoredValidation(Validation):

    def __init__(self, exceptions=None):
        if exceptions is None:
            self.stored_exceptions = []

    def exceptions(self):
        return self.stored_exceptions

# class ValidationSet(Validation):?


class SubjectValidation(Validation):
    def __init__(self, subject, fhandle, httpcache=None):
        self.subject = subject
        self.fhandle = fhandle
        if isinstance(httpcache, bald.HttpCache):
            self.cache = httpcache
        else:
            self.cache = bald.HttpCache()

    def is_valid(self):
        return not self.exceptions()

    def exceptions(self):
        exceptions = []
        exceptions = self.check_attr_uris(exceptions)
        exceptions = self.check_attr_domain_range(exceptions)
        exceptions = self._extra_exceptions(exceptions)
        return exceptions

    def _extra_exceptions(self, exceptions):
        return exceptions

    def check_attr_uris(self, exceptions):
        def _check_uri(uri, exceptions):
            if not self.cache.check_uri(uri):
                msg = '{} is not resolving as a resource (404).'
                msg = msg.format(uri)
                exceptions.append(ValueError(msg))
            return exceptions

        for pref, uri in self.subject.prefixes().iteritems():
            exceptions = _check_uri(self.subject.unpack_uri(uri),
                                    exceptions)
        for alias, uri in self.subject.aliases.iteritems():
            exceptions = _check_uri(self.subject.unpack_uri(uri),
                                    exceptions)
        for attr, value in self.subject.attrs.iteritems():
            exceptions = _check_uri(self.subject.unpack_uri(attr),
                                    exceptions)
            if isinstance(value, str):
                val = self.subject.unpack_uri(value)
                if self.cache.is_http_uri(val):
                    exceptions = _check_uri(val, exceptions)
        return exceptions

    def check_attr_domain_range(self, exceptions):
        for attr, value in self.subject.attrs.iteritems():
            uri = self.subject.unpack_uri(attr)
            if self.cache.check_uri(uri):
                # thus we have a payload
                # go rdf
                g = rdflib.Graph()
                data=self.cache[uri].text
                try:
                    g.parse(data=self.cache[uri].text, format="n3")
                except Exception, e:
                    g.parse(data=self.cache[uri].text, format="xml")
                query = ('SELECT ?s \n'
                         '(GROUP_CONCAT(?domain; SEPARATOR=" | ") AS ?domains)'
                         ' \n'
                         '(GROUP_CONCAT(?type; SEPARATOR=" | ") AS ?types) \n'
                         'WHERE {{ \n'
                         '?s a ?type . \n'
                         'OPTIONAL{{ ?s rdfs:domain ?domain . }} \n'
                         'FILTER(?s = <{uria}> || ?s = <{urib}>) \n'
                         '}} \n'
                         'GROUP BY ?s \n'.format(uria=uri,
                                                 urib=uri.rstrip('/')))
                qres = list(g.query(query))
                if len(qres) != 1:
                    raise ValueError('{} does not define one and only one \n'
                                     'rdfs:domain'.format(uri))
                qres, = qres
                # implement recursive inheritance check
                # we need to check if the value that the attr points to
                # has an rdf:type which is the same as the one required by
                # the object property constraint
                # The value may be a URI or it may be a reference to another
                # subject within the file.
                # therefore subjects in the file have to be typed?!?

                # import pdb; pdb.set_trace()
                # if qres.domains != rdflib.term.URIRef(value):
                #     msg = ('The attribute {} references ')
                #     exceptions.appen(ValueError(msg))
        return exceptions


class ContainerValidation(SubjectValidation):

    def __init__(self, **kwargs):
        super(ContainerValidation, self).__init__(**kwargs)


class ArrayValidation(SubjectValidation):

    def __init__(self, name, array, **kwargs):
        self.array = array
        self.name = name
        super(ArrayValidation, self).__init__(**kwargs)

    def _extra_exceptions(self, exceptions):
        exceptions = self.check_array_references(exceptions)
        return exceptions

    def check_array_references(self, exceptions):
        def _check_ref(parraysubj, parray, carraysubj, carray):
            if not valid_array_reference(parray, carray):
                msg = ('{} declares a child of {} but the arrays'
                       'do not conform to the bald array reference'
                       'rules')
                msg = msg.format(parraysubj, carraysubj)
                exceptions.append(ValueError(msg))
            return exceptions

        # if this Array has a bald__references
        # not implemented yet: and it's a singleton
        if self.subject.attrs.get('bald__references', ''):
            # then it must have a bald_array
            ref_dset = self.fhandle[self.subject.attrs.get('bald__references')]
            child_dset = None
            if (hasattr(ref_dset, 'attrs')):
                child_dset = self.fhandle[ref_dset.attrs.get('bald__array', None)]
            elif 'bald__array' in ref_dset.ncattrs():
                child_dset = self.fhandle[ref_dset.bald__array]
            else:
                exceptions.append(ValueError('A bald__Reference must link to '
                                             'one and only one bald__Array'))
            # and we impose bald broadcasting rules on it
            parray = np.zeros(self.array.shape)
            carray = np.zeros(child_dset.shape)

            exceptions = _check_ref('p', parray, 'c', carray)

        return exceptions


class ValidationSet(Validation):
    pass


class ValidationList(Validation):
    pass
