import expressions
from draw import *

padding = 25

class Stickfigure(Primitive):
    def __init__(self):
        self.set_name("figure")
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
        self.head.d = self.height / 5
        self.body.height = self.head.d * 2
        self.legs[0].height = self.legs[1].height = self.head.d * 2
        
        # Widths
        self.arms.width = self.width 
        self.legs[0].pt2.x = self.x - self.width/3
        self.legs[1].pt2.x = self.x + self.width/3
        
        # Edges
        self.left = self.arms.pt1.x
        self.right = self.arms.pt2.x
        self.x = self.head.bottom.x
        self.floor = self.head.bottom.y + self.head.d * 4

class Panel(Box):
    def __init__(self,n_figures=1):
        super().__init__()
        self.set_name("panel")
        self.figures = Array(n_figures, Stickfigure)
        for idx,figure in enumerate(self.figures):
            figure.floor = self.bottom.y - self.height/10
            figure.height = figure.width * 7/3
        padding = self.width/3 if n_figures==1 else self.width/8
        spacing = self.width/10
        for a,b in self.figures.adj_objs():
            b.left = a.right + spacing
            b.width = a.width
        self.figures[0].left = self.left.x + padding
        self.figures[-1].right = self.right.x - padding

# panel = Panel(2)
# panel.topleft = Point(padding,padding)
# panel.width = panel.height = 200
# print(panel.sim_draw())
# display(panel)

class Strip(Primitive):
    def __init__(self):
        self.panelwidth = self.panelheight = 200
        N = 3
        step = 2
        self.panels = InitorArray(Panel,*zip(range(1,step*N+1,step)))
        self.topleft = self.panels.first.topleft = Point(padding,padding)
        for panel in self.panels:
            panel.width = self.panelwidth
            panel.height= self.panelheight
        for a,b in self.panels.adj_objs():
            a.right = b.left

#display(Strip(1,300),w=400,h=300)
#print(Strip(1,300).sim_draw())
        
#print(Strip().sim_draw())
display(Strip(),w=650,h=250)
