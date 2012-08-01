# Pylogram libraries
from expressions import constrain, Contradiction, Var, evaluate
from object import *
from helpers import *
import tkinter

class Primitive(Obj):
    def __init__(self,name=""):
        self._name = name # Not used?
        
    def sim_draw(self, str=""):
        return self.reduce_subobjs('sim_draw', str)
        
    def draw(self, canvas):
        return self.reduce_subobjs('draw',canvas)
        
    def dump_undefined(self):
        pass

class Point(Primitive):
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
    
class Line(Primitive):
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
        self.width = self.pt2.x - self.pt1.x
        self.height= self.pt2.y - self.pt1.y
        self.mid = self.pt1 + Point(self.width/2,self.height/2)

    def draw(self, canvas):
        canvas.create_line(int(evaluate(self.pt1.x)),
                           int(evaluate(self.pt1.y)),
                           int(evaluate(self.pt2.x)),
                           int(evaluate(self.pt2.y)))        
        return canvas
        
    def sim_draw(self, str=""):
        return str + " >> Drawing line from {:},{:} to {:},{:}\n".format(self.pt1.x,self.pt1.y,self.pt2.x,self.pt2.y)
        
class Circle(Primitive):
    def __init__(self, name=""):
        self.r = Var(name+'.r')
        self.d = self.r * 2
        self.c = Point(name=name+'.c')
        self.bottom = self.c + Point(0, self.r)
        self.top    = self.c + Point(0,-self.r)
        self.left   = self.c + Point(-self.r, 0)
        self.right  = self.c + Point( self.r, 0)

    def draw(self, canvas):
        canvas.create_oval(int(evaluate(self.c.x))-int(evaluate(self.r)),
                           int(evaluate(self.c.y))-int(evaluate(self.r)),
                           int(evaluate(self.c.x))+int(evaluate(self.r)),
                           int(evaluate(self.c.y))+int(evaluate(self.r)))  
        return canvas

    def sim_draw(self, str=""):
        return str + " >> Drawing circle about {:},{:} with radius {:}\n".format(self.c.x,self.c.y,self.r)


class hLine(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = self.pt1.y = self.pt2.y

class vLine(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = self.pt1.x = self.pt2.x

class Box(Primitive):
    def __init__(self, name=""):
        self.top = hLine(name="top")
        self.bottom = hLine(name="bottom")
        self.left = vLine(self.top.pt1, self.bottom.pt1, name="left")
        self.right = vLine(self.top.pt2, self.bottom.pt2, name="right")
        self.topleft = self.top.pt1
        self.topright = self.top.pt2
        self.bottomleft = self.bottom.pt1
        self.bottomright = self.bottom.pt2
        self.width = self.top.width
        self.height = self.left.height
        
class Square(Box):
    def __init__(self,name=""):
        super().__init__(name=name)
        self.width = self.height
        
def display(*objs, w=300,h=300):
    master = tkinter.Tk()
    canvas = tkinter.Canvas(master, width=w, height=h)
    for obj in objs:
        obj.draw(canvas)
    canvas.pack()
    tkinter.mainloop()