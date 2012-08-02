# Standard modules
from numbers import Number
from collections import defaultdict
from itertools import zip_longest, chain, repeat
from fractions import Fraction
from functools import partial
class Struct:
    pass

DefaultArg = Struct
        
class nonzero_dict( defaultdict ):
    def __init__(self, *args):
        super().__init__(int, *args)
        
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

def first( *its ):
    return next( chain(*its) )
    
def count( it ):
    return len(tuple(it))

def ignore(*args):
    pass

def undef_eq(list1, list2):
    ret = True
    sentinel = DefaultArg()
    for a,b in zip_longest(list1,list2):
        if a is sentinel or b is sentinel: return False
        ret = ret & (a==b)
        if ret==False: return False
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

def if_raises( exception, func, *args, **kwargs):
    try:
        func(*args,**kwargs)
        return True
    except exception:
        return False

class OutsideBounds:
    def __getattr__(self,attr):
        return self
    def __call__(self,*args):
        return self
    
_outside_bounds = OutsideBounds()
        
class _each_base:
    def __init__(self,arr,enumerate_other=iter, enumerate_self=iter):
        self.__dict__['_arr'] = arr
        self.__dict__['_enumerate_other'] = enumerate_other
        self.__dict__['_enumerate_self'] = enumerate_self
    
    def __call__(self,*args):
        return type(self)( [ item(*args) for item in self ] , enumerate_other = self._enumerate_other )
    
    def __iter__(self):
        return self._enumerate_self(self._arr)
    
    def __getattr__(self,attr):
        if attr=='val':
            return self
        else:
            return type(self)( [ getattr(item,attr) for item in self ] , enumerate_other = self._enumerate_other )
            
    def __getitem__(self,idx):
        return self._arr[idx]
            
    def __setattr__(self,attr,other):
        for i,(_,val) in enumerate(zip(self._arr,self._enumerate_other(other))):
            if self._arr[i] is not _outside_bounds and val is not _outside_bounds:
                if attr=='val':
                    self._arr[i] = val
                else:
                    setattr(self._arr[i],attr,val)
    
    def __mul__(self,other): return self.__getattr__('__mul__')(other)
    def __rmul__(self,other): return self.__getattr__('__rmul__')(other)
    def __add__(self,other): return self.__getattr__('__add__')(other)
    def __radd__(self,other): return self.__getattr__('__radd__')(other)
    def __sub__(self,other): return self.__getattr__('__sub__')(other)
    def __rsub__(self,other): return self.__getattr__('__rsub__')(other)
    def __truediv__(self,other): return self.__getattr__('__truediv__')(other)
    def __pow__(self,other): return self.__getattr__('__pow__')(other)

def each(arr):
    return _each_base(arr)
    
def every(arr):
    return _each_base(arr,enumerate_other=repeat)
    
def prev(arr):
    return _each_base( [_outside_bounds]+arr[:-1] )