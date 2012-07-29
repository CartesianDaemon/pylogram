# Pylogram libraries
import pylogram
from pylogram import constrain, Contradiction, Var
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
                pylogram.Expr(self._vars[attr]).constrain_equal( val )
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
                pylogram.Expr(a).constrain_equal(b)

    def __setitem__(self, emptyslice, rhs):
        # Support "a [:]= b" syntax
        assert emptyslice == slice(None, None, None)
        self.constrain_equal(rhs)

class Point(Obj):
    def __init__(self, *args, prefix=""):
        if len(args)==0:
            self.x = Var(prefix+'.x')
            self.y = Var(prefix+'.y')
        else:
            assert len(args)==2
            self.x, self.y = args
        
    def __add__(self,other):
        assert isinstance(other,Point)
        return Point( self.x+other.x, self.y+other.y )

class Line(Obj):
    def __init__(self, prefix=""):
        super().__init__()
        self.pt1 = Point(prefix=prefix+".pt1")
        self.pt2 = Point(prefix=prefix+".pt2")
        
class Circle(Obj):
    def __init__(self, prefix=""):
        self.r = Var(prefix+'.r')
        self.d = self.r * 2
        self.c = Point(prefix=prefix+'.c')
        self.bottom = self.c + Point(0, self.r)
        self.top    = self.c + Point(0,-self.r)
        self.left   = self.c + Point(-self.r, 0)
        self.right  = self.c + Point( self.r, 0)
        
        