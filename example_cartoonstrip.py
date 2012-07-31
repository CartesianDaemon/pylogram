import expressions
from draw import *

padding = 25

class Stickfigure(Primitive):
    def __init__(self):
        # Primitives
        self.head = Circle()
        self.body = vLine()
        self.arms = hLine()
        self.legs = Array(2,Line)
        # Joints
        self.head.bottom = self.body.pt1
        self.body.pt2 = self.legs[0].pt1 = self.legs[1].pt1
        self.arms.mid = self.head.bottom + Point(0,self.height/10)
        #Heights
        self.head.d = self.height / 7
        self.body.height = self.head.d * 3
        self.legs[0].height = self.legs[1].height = self.head.d * 3
        # Widths
        self.arms.width = self.width
        self.legs[1].x = self.legs[0].x + self.width/2
        # Edges
        self.x = self.body.x
        self.floor = self.legs[0].pt2.y


class Panel(Box):
    def __init__(self,*args,stickfigures=0):
        super().__init__(*args)
        self.figure = Stickfigure()
        self.figure.floor = self.bottom.y - self.height/10
        self.figure.x = self.left.x + self.width/2
        self.figure.width = self.width /4
        self.figure.height = self.figure.width * 3
        self.set_name("panel")

panel = Panel()
panel.topleft = Point(padding,padding)
panel.width = panel.height = 100
print("\n".join( str(expr) for expr in expressions.constraints()))
print("\n".join( str(expr) for expr in expressions.variables()))
display(panel)

class Strip(Array):
    def __init__(self, N, width = 100, height=100):
        super().__init__(N,Panel)
        self.topleft = self.first.topleft = Point(padding,padding)
        self.first.width = width / N
        #(self.first.width * N) [:]= width
        for a in self:
            self.panelwidth = a.width
            self.height = a.height = height # self.height = self.all.height
        for a,b in self.adj_objs():
            a.right = b.left

#display(Strip(1,300),w=400,h=300)
#print(Strip(1,300).sim_draw())
        
# display(Strip(3,600, 200),w=650,h=250)

