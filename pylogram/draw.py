# Pylogram libraries
from excpt import *
from expressions import constrain, Var, evaluate
from object import *
from helpers import *
import Tkinter as tkinter
#import tkinter
import Image, ImageDraw

def conv(expr):
    return int(evaluate(expr)+0.5)

class Primitive(Obj):
    def __init__(self,name=""):
        self._name = name # Not used?
        
    def sim_draw(self, str=""):
        return self.reduce_subobjs('sim_draw', str)
        
    def draw_tk(self, canvas):
        return self.reduce_subobjs('draw_tk',canvas)
        
    def draw_pil(self, draw):
        return self.reduce_subobjs('draw_pil',draw)
        
    def dump_undefined(self):
        pass

default_coord_type = Fraction
        
class Point(Primitive):
    def __init__(self, *args,**kwargs):
        name = kwargs.get('name',"")
        if len(args)==0:
            self.x = Var(name+'.x',prefer=default_coord_type)
            self.y = Var(name+'.y',prefer=default_coord_type)
        elif len(args)==1:
            assert isinstance(args[0],str)
            self.__init__(name=args[0])
        else:
            assert len(args)==2
            self.x, self.y = args
        
    def __add__(self,other):
        assert isinstance(other,Point)
        return Point( self.x+other.x, self.y+other.y )
    
    def draw_tk(self, canvas):
        return canvas
        
    def draw_pil(self, draw):
        return draw
        
    def sim_draw(self, str=""):
        return str
        
    def __repr__(self):
        return "<Point " + repr(self.x) + "," + repr(self.y) + ">"
 
class Circle(Primitive):
    def __init__(self,name="",**kwargs):
        self.r = Var(name+'.r',prefer=default_coord_type)
        self.d = self.r * 2
        self.c = Point(name=name+'.c')
        self.bottom = self.c + Point(0, self.r)
        self.top    = self.c + Point(0,-self.r)
        self.left   = self.c + Point(-self.r, 0)
        self.right  = self.c + Point( self.r, 0)
        self._col = kwargs.get('col',"black")

    def draw_tk(self, canvas):
        canvas.create_oval(conv(self.c.x)-conv(self.r),
                           conv(self.c.y)-conv(self.r),
                           conv(self.c.x)+conv(self.r),
                           conv(self.c.y)+conv(self.r))  
        return canvas

    def draw_pil(self, draw):
        draw.ellipse((conv(self.c.x)-conv(self.r),
                      conv(self.c.y)-conv(self.r),
                      conv(self.c.x)+conv(self.r),
                      conv(self.c.y)+conv(self.r)), outline=self._col)
        return draw

    def sim_draw(self, str=""):
        return str + " >> Drawing circle about {:},{:} with radius {:}\n".format(int(evaluate(self.c.x)),int(evaluate(self.c.y)),int(evaluate(self.r)))

class Text(Primitive):
    def __init__(self,text="",anchor='sw',**kwargs):
        self._text = text
        self.pt = Point()
        self._anchor = anchor
        self._col = kwargs.get('col',"black")
       
    def sim_draw(self, str=""):
        if self._text:
            return str + ' >> Drawing "'+self._text+'" at {:},{:}\n"'.format(int(evaluate(self.pt.x)),int(evaluate(self.pt.y)))
        
    def draw_tk(self,canvas):
        if self._text:
            canvas.create_text(int(evaluate(self.pt.x)),int(evaluate(self.pt.y)),text=self._text,anchor=self._anchor)
        return canvas

    def draw_pil(self,draw):
        if self._text:
            sz = draw.textsize(self._text)
            draw.text((int(evaluate(self.pt.x)),int(evaluate(self.pt.y))-sz[1]),self._text, fill = self._col)
        return draw

class Line(Primitive):
    def __init__(self, *args, **kwargs):
        name = kwargs.get('name',"")
        self._col = kwargs.get('col',"black")
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

    def draw_tk(self, canvas):
        canvas.create_line(int(evaluate(self.pt1.x)),
                           int(evaluate(self.pt1.y)),
                           int(evaluate(self.pt2.x)),
                           int(evaluate(self.pt2.y)), fill = self._col)        
        return canvas
        
    def draw_pil(self, draw):
        draw.line((int(evaluate(self.pt1.x)),
                   int(evaluate(self.pt1.y)),
                   int(evaluate(self.pt2.x)),
                   int(evaluate(self.pt2.y))), fill = self._col)
        return draw

    def sim_draw(self, str=""):
        return str + " >> Drawing line from {:},{:} to {:},{:}\n".format(int(evaluate(self.pt1.x)),int(evaluate(self.pt1.y)),
                                                                         int(evaluate(self.pt2.x)),int(evaluate(self.pt2.y)))
        
class hLine(Line):
    def __init__(self, *args, **kwargs):
        super(hLine,self).__init__(*args, **kwargs)
        self.y = self.pt1.y = self.pt2.y

class vLine(Line):
    def __init__(self, *args, **kwargs):
        super(vLine,self).__init__(*args, **kwargs)
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
        super(Square,self).__init__(name=name)
        self.width = self.height

def display(*objs, **kwargs):
    w = kwargs.get('w',300)
    h = kwargs.get('h',300)
    master = tkinter.Tk()
    canvas = tkinter.Canvas(master, width=w, height=h)
    for obj in objs:
        if obj.free_vars():
            print(set(obj.free_vars()))
        obj.draw_tk(canvas)
    canvas.pack()
    tkinter.mainloop()
    
def create_image(*objs, **kwargs):
    w = kwargs.get('w',300)
    h = kwargs.get('h',300)
    image = Image.new('RGB',(w,h),(255,255,255))
    draw = ImageDraw.Draw(image)
    for obj in objs:
        if obj.free_vars():
            print(set(obj.free_vars()))
        obj.draw_pil(draw)
    del draw
    return image
    