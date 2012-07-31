# Pylogram libraries
import pylogram
import pylogram as pyl
from pylogram import constrain, Contradiction, Var
from helpers import *
import tkinter

def is_obj(obj):
    return isinstance(obj,Obj)

class Obj:
    def __init__(self,name=""):
        self._name = name # Not used?
        
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

    def sim_draw(self, str=""):
        return self.reduce_subobjs('sim_draw', str)
        
    def draw(self, canvas):
        return self.reduce_subobjs('draw',canvas)
    
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

class Point(Obj):
    def __init__(self, *args, name=""):
        if len(args)==0:
            self.x = Var(name+'.x')
            self.y = Var(name+'.y')
        elif len(args)==1:
            assert isinstance(args[0],str)
            self.__init__(name=args[0])
        else:
            assert len(args)==2
            self.x, self.y = args
        
    def __add__(self,other):
        assert isinstance(other,Point)
        return Point( self.x+other.x, self.y+other.y )
    
    def draw(self, canvas):
        return canvas
        
    def sim_draw(self, str=""):
        return str
    
class Line(Obj):
    def __init__(self, *args, name=""):
        if len(args)==0:
            self.pt1 = Point(name=name+".pt1")
            self.pt2 = Point(name=name+".pt2")
        elif len(args)==1:
            if isinstance(args[0],str):
                self.__init__(name=args[0])
            elif isinstance(args[0],Point):
                self.pt1 = args[0]
                self.pt2 = Point(name=name+".pt2")
        else:
            assert len(args)==2
            self.pt1, self.pt2 = args

    def draw(self, canvas):
        canvas.create_line(int(pyl.evaluate(self.pt1.x)),
                           int(pyl.evaluate(self.pt1.y)),
                           int(pyl.evaluate(self.pt2.x)),
                           int(pyl.evaluate(self.pt2.y)))        
        return canvas
        
    def sim_draw(self, str=""):
        return str + " >> Drawing line from {:},{:} to {:},{:}\n".format(self.pt1.x,self.pt1.y,self.pt2.x,self.pt2.y)
        
class Circle(Obj):
    def __init__(self, name=""):
        self.r = Var(name+'.r')
        self.d = self.r * 2
        self.c = Point(name=name+'.c')
        self.bottom = self.c + Point(0, self.r)
        self.top    = self.c + Point(0,-self.r)
        self.left   = self.c + Point(-self.r, 0)
        self.right  = self.c + Point( self.r, 0)

    def draw(self, canvas):
        canvas.create_oval(pyl.evaluate(self.c.x)-pyl.evaluate(self.r),
                           pyl.evaluate(self.c.y)-pyl.evaluate(self.r),
                           pyl.evaluate(self.c.x)+pyl.evaluate(self.r),
                           pyl.evaluate(self.c.y)+pyl.evaluate(self.r))  
        return canvas

    def sim_draw(self, str=""):
        return str + " >> Drawing circle about {:},{:} with radius {:}\n".format(self.c.x,self.c.y,self.r)


class hLine(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = self.pt1.y = self.pt2.y
        self.length = self.pt2.x - self.pt1.x
        self.pt1.y
        
class vLine(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = self.pt1.x = self.pt2.x
        self.length = self.pt2.y - self.pt1.y

class Box(Obj):
    def __init__(self, name=""):
        self.top = hLine(name="top")
        self.bottom = hLine(name="bottom")
        self.left = vLine(self.top.pt1, self.bottom.pt1, name="left")
        self.right = vLine(self.top.pt2, self.bottom.pt2, name="right")
        self.topleft = self.top.pt1
        self.topright = self.top.pt2
        self.bottomleft = self.bottom.pt1
        self.bottomright = self.bottom.pt2
        self.width = self.top.length
        self.height = self.left.length
        
class Square(Box):
    def __init__(self,name=""):
        super().__init__(name=name)
        self.width = self.height
        
def display(*objs, w=300,h=300):
    master = tkinter.Tk()
    canvas = tkinter.Canvas(master, width=w, height=h)
    for obj in objs: obj.draw(canvas)
    canvas.pack()
    tkinter.mainloop()