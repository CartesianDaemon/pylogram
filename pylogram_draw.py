import pylogram
from pylogram import constrain, Contradiction, Var

def is_obj(obj):
    return isinstance(obj,Obj)

class Obj:
    def __init__(self):
        # Access members via dict until _vars is set up, else setattr puts getattr into infinite loop
        self.__dict__['_vars'] = {}
            
    def __setattr__(self,attr,val):
        if attr in self._vars:
            pylogram.Expr(self._vars[attr]).constrain_equal( val )
        else:
            self._vars[attr] = val
    
    def __getattr__(self,attr):
        return self._vars[attr]

    def constrain_equal(self,other):
        assert is_obj(other)
        assert self._vars.keys() == other._vars.keys()
        for a,b in zip():
            if is_obj(a):
                a.constrain_equal(b)
            else:
                Expr(a).constrain_equal(b)

    def __setitem__(self, emptyslice, rhs):
        # Support "a [:]= b" syntax
        assert emptyslice == slice(None, None, None)
        self.constrain_equal(rhs)
        return Equ(self,rhs)
