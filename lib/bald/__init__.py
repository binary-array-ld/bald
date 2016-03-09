import h5py

import bald.validation


@contextlib.contextmanager
def load(afilepath):
    if afilepath.endswith('.hdf5'):
        loader = h5py.File
    else:
        raise ValueError('filepath suffix not supported')
    try:
        f = loader(afilepath, "r")
        yield f
    finally:
        f.close()
    return f

def validate(afilepath):
    """
    Validate a file with respect ot binarry-array-linked-data.
    Returns a :class:`bald.validation.Validation` 
    """
    
    with load(afilepath) as f:
        
    
