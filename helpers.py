# Standard modules
from numbers import Number
from collections import defaultdict
from itertools import zip_longest
from fractions import Fraction

class Struct:
    pass

DefaultArg = Struct
        
class nonzero_dict( defaultdict ):
    def __init__(self):
        super().__init__(int)
        
    def keys(self):
        return { k for k,v in super().items() if v }

    def items(self):
        return { (k,v) for k,v in super().items() if v }
    
    def values(self):
        return { v for v in super().values() if v }
    
    def __len__(self):
        return count(self.keys())

    def __repr__(self):
        return repr(dict(self))
        
    def __bool__(self):
        return bool(self.keys())

def first( it ):
    return next( iter(it) )
    
def count( it ):
    return len(tuple(it))
    
def variables(constraints):
    return set().union( * ( equ.variables() for equ in constraints ) )

def ignore(*args):
    pass

def undef_eq(list1, list2):
    ret = True
    sentinel = DefaultArg()
    for a,b in zip_longest(list1,list2):
        if a is sentinel or b is sentinel: return False
        ret = ret & (a==b)
        # if ret==False: return False
    return ret # True or _Undefined()

def mod_n(a,p):
    return a if p is None else a % p
    
def inverse_mod_n(a, p):
    if p is None: return Fraction(1,a)
    a = a % p
    r = a
    d = 1
    for _ in range(p):
        d = ((p // r + 1) * d) % p
        r = (d * a) % p
        if r == 1:
            break
    else:
        raise ValueError('%d has no inverse mod %d' % (a, p))
    return d
