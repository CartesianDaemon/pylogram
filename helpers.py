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

class nonzero_dict( defaultdict ): #TODO: Move int onto this line?
    def __init__(self):
        super(nonzero_dict,self)
        super(nonzero_dict,self).__init__(int)
        
    def keys(self):
        return { k for k,v in super(nonzero_dict,self).items() if v }

    def items(self):
        return { (k,v) for k,v in super(nonzero_dict,self).items() if v }
    
    def values(self):
        return { v for v in super(nonzero_dict,self).values() if v }
    
    def __len__(self):
        return count(self.keys())

    def __repr__(self):
        # TODO: delegate to super(super(self))
        return repr(dict(self))
        
    def __bool__(self):
        return bool(self.keys())

        
def solve_matrix(A,b):
    try:
        return np.linalg.solve(A,b)
    except np.linalg.LinAlgError:
        return tuple( None for _ in b )

def first( it ):
    return next( iter(it) )
    
def count( it ):
    return len(tuple(it))