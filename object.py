# Pylogram libraries
import expressions
import expressions as pyl
from expressions import constrain, Contradiction, Var
from helpers import *

def is_obj(obj):
    return isinstance(obj,Obj)

class Obj:
    def __setattr__(self,attr,val):
        if '_vars' not in self.__dict__: self.__dict__['_vars'] = {}
        if attr in self._vars:
            if is_obj(self._vars[attr]):
                self._vars[attr].constrain_equal( val )
            else:
                pyl.Expr(self._vars[attr]).constrain_equal( val )
        elif attr[0]=="_":
            self.__dict__[attr] = val
        else:
            self._vars[attr] = val
    
    def __getattr__(self,attr):
        return self._vars[attr]
        
    def __eq__(self,other):
        return is_obj(other) and self._vars.keys() == other._vars.keys() and undef_eq(self._vars.values(),other._vars.values())

    def constrain_equal(self,other):
        assert is_obj(other)
        assert self._vars.keys() == other._vars.keys()
        for a,b in zip(self._vars.values(),other._vars.values()):
            if is_obj(a):
                a.constrain_equal(b)
            else:
                pyl.Expr(a).constrain_equal(b)

    def __setitem__(self, emptyslice, rhs):
        # Support "a [:]= b" syntax
        assert emptyslice == slice(None, None, None)
        self.constrain_equal(rhs)
    
    def reduce_subobj(self, subobj, subfunc, arg):
        # TODO: Use try/except.
        if is_obj(subobj):
            return getattr(subobj,subfunc)(arg)
        else:
            # TODO: For undef and similar make this function into an "all"
            # Literals, Vars and anything else won't be drawn on screen
            return arg
    
    def reduce_subobjs(self, subfunc, arg):
        assert type(self) != type(Obj()) # Should be derived class, not Obj itself, else will recurse
        for subobj in self._vars.values():
            arg = self.reduce_subobj( subobj, subfunc, arg )
        return arg

class Array(Obj):
    def __init__(self,N,Type,name=""):
        # TODO: Do we want to support non-var use, eg. arr1 = Array(N); arr1.first = 1; arr1.each = arr1.prev*2
        self.N = N
        self._arr = [ Type(name=name+"["+str(idx)+"]") for idx in range(N) ]
        self.first = self._arr[0]
        self.last = self._arr[-1]

    def __setitem__(self,idx,val):
        if idx==slice(None, None, None):
            super().__setitem__(idx,val)
        else:
            assert 0 <= idx <= self.N
            self._arr[idx].constrain_equal(val)
        
    def __getitem__(self,idx):
        return self._arr[idx]
        
    def adj_objs(self, n=2):
        return ( self._arr[i:i+n] for i in range(self.N+1-n) )

    def __iter__(self):
        return iter(self._arr)
        
    def __repr__(self):
        return repr(self._arr)
        
    def __eq__(self,other):
        return undef_eq( self, other )

    def reduce_subobjs(self, subfunc, arg):
        # assert type(self) == type(Array()) 
        for subobj in self._arr:
            arg = self.reduce_subobj(  subobj, subfunc, arg )
        for subobj in self._vars.values():
            arg = self.reduce_subobj(  subobj, subfunc, arg )
        return arg
