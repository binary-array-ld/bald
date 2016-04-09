
import numpy as np

import bald


def valid_array_reference(parray, carray):
    """
    Returns boolean.
    Validates bald array broadcasting rules between a parent array and a child array.

    Args:
        * parray - a numpy array: the parent of a bald array reference relation

        * carray - a numpy array: the child of a bald array reference relation 
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

class SubjectValidation(Validation):

    def __init__(self, subject, httpcache=None): 
        self.subject = subject
        if isinstance(httpcache, bald.HttpStatusCache):
            self.cache = httpcache
        else:
            self.cache = bald.HttpStatusCache()
            

    def is_valid(self):
        return not self.exceptions()
        
    def exceptions(self):
        exceptions = []
        exceptions = self.check_attr_uris(exceptions)
        exceptions = self.check_attr_domain_range(exceptions)
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
        for attr, value in self.subject.attrs.iteritems():
            exceptions = _check_uri(self.subject.unpack_uri(attr),
                                    exceptions)
            if isinstance(value, str):
                exceptions = _check_uri(self.subject.unpack_uri(value),
                                        exceptions)
        return exceptions

    def check_attr_domain_range(self, exceptions):
        return exceptions
    

class ContainerValidation(SubjectValidation):

    def __init__(self, **kwargs):
        super(ContainerValidation, self).__init__(**kwargs)

    def exceptions(self):
        exceptions = []
        exceptions = self.check_attr_uris(exceptions)
        return exceptions

class DatasetValidation(SubjectValidation):


    def __init__(self, name, dataset, fhandle, **kwargs):
        
        self.dataset = dataset
        self.name = name
        self.fhandle = fhandle
        super(DatasetValidation, self).__init__(**kwargs)

    def exceptions(self):
        exceptions = []
        exceptions = self.check_attr_uris(exceptions)
        exceptions = self.check_array_references(exceptions)
        return exceptions

    def check_array_references(self, exceptions):
        def _check_ref(pdataset, parray, cdataset, carray):
            if not valid_array_reference(parray, carray):
                msg = ('{} declares a child of {} but the arrays'
                       'do not conform to the bald array reference'
                       'rules')
                msg = msg.format(pdataset, cdataset)
                exceptions.append(ValueError(msg))
            return exceptions

        for attr, value in self.subject.attrs.iteritems():
            # should support subtypes
            if attr == 'bald_._reference':
                # check if it's this type, otherwise exception)
                # if isinstance(value,
                child_dset = self.fhandle[value]
                parray = np.zeros(self.dataset.shape)
                carray = np.zeros(child_dset.shape)
        
                exceptions = _check_ref('p', parray, 'c', carray)
        return exceptions


class ValidationSet(Validation):
    pass

class ValidationList(Validation):
    pass


