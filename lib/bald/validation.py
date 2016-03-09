
import requests

import bald

def check_uri(uri):
    result = False
    if uri.startswith('http://') or uri.startswith('https://'):
        r = requests.get(uri)
        if r.status_code == 200:
            headers={'Accept':'text/turtle'}
            rraw = requests.get(uri, headers=headers)
            if rraw.status_code == 200:
                result = True
    return result



class Validation(object):
                 
    def is_valid(self):
        return not self.exceptions()
        
    def exceptions(self):
        exceptions = []
        return exceptions

class ContainerValidation(Validation):
    def __init__(self, container):
        self.container = container

    def is_valid(self):
        return not self.exceptions()
        
    def exceptions(self):
        exceptions = []
        exceptions = self.check_attr_uris(exceptions)
        return exceptions

    def check_attr_uris(self, exceptions):
        def _check_uri(uri, exceptions):
            if not check_uri(uri):
                msg = '{} is not resolving as a resource (404).'
                msg = msg.format(uri)
                exceptions.append(ValueError(msg))
            return exceptions

        for pref, uri in self.container.prefixes().iteritems():
            exceptions = _check_uri(self.container.unpack_uri(uri),
                                    exceptions)
        for attr, value in self.container.attrs.iteritems():
            exceptions = _check_uri(self.container.unpack_uri(attr),
                                    exceptions)
            exceptions = _check_uri(self.container.unpack_uri(value),
                                    exceptions)

        return exceptions
    
            

class ValidationSet(Validation):
    pass

class ValidationList(Validation):
    pass



#if __name__ == '__main__':
