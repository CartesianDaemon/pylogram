# Standard modules
from numbers import Number
from collections import defaultdict

# Numpy libraries
import numpy as np

class Struct:
    pass
    
DefaultArg = Struct()

def is_0(term):
    return is_x(term,0)

def is_1(term):
    return is_x(term,1)

def is_x(term, i):
    # return val is 1 works in CPython for -8<=1<=256 but not portable
    assert isinstance(i,Number)
    if isinstance(term,Number):
        assert( term == i )
        return True
    else:
        return False
        
def is_num(term):
    return isinstance(term,Number)

class nonzero_dict( defaultdict ):
    def __init__(self):
        super(nonzero_dict,self)
        super(nonzero_dict,self).__init__(int)

    def __setitem__(self, key, value):
        assert isinstance(value, Number)
        if value != 0:
            super(nonzero_dict, self).__setitem__(key, value)
        elif key in self:
            del self[key]
            # del super(nonzero_dict, self)[key]
            
    def __repr__(self):
        # TODO: delegate to super(super(self))
        return repr(dict(self))

        
def solve(A,b):
    try:
        return np.linalg.solve(A,b)
    except np.linalg.LinAlgError:
        return ( None for _ in b )
