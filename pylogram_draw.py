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
            if is_obj(self._vars[attr]):
                self._vars[attr].constrain_equal( val )
            else:
                pylogram.Expr(self._vars[attr]).constrain_equal( val )
        else:
            self._vars[attr] = val
    
    def __getattr__(self,attr):
        return self._vars[attr]
        
    def __eq__(self,other):
        return is_obj(other) and all( a==b for a,b in zip(self._vars.values(),other._vars.values()) )

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
    def __init__(self, *args):
        super().__init__()
        self.x = Var()
        self.y = Var()
        assert len(args) in (0,2)
        for coord, arg in zip((self.x,self.y),args):
            coord [:]= arg 
        
    def __add__(self,other):
        assert isinstance(other,Point)
        return Point( self.x+other.x, self.y+other.y )

class Line(Obj):
    def __init__(self):
        super().__init__()
        self.pt1 = Point()
        self.pt2 = Point()
        
class Circle(Obj):
    def __init__(self):
        super().__init__()
        self.r = Var()
        self.d = self.r * 2
        self.c = self.center = Point()
        self.bottom = self.c + Point(0, self.r)
        self.top    = self.c + Point(0,-self.r)
        self.left   = self.c + Point(-self.r, 0)
        self.right  = self.c + Point( self.r, 0)
        
        