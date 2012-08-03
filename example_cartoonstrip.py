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
        
class SpeechBubble(Primitive):
    def __init__(self,text="",pack=''):
        self.textbox = Text(text=text,anchor='s'+pack)
        self.line = vLine()
        self.line.pt1.y = self.textbox.pt.y + 10
        self.headtop = self.line.pt2 + Point(0,10)
        if pack=='':
            self.textbox.pt.x = self.line.x
        elif pack=='w':
            self.textbox.pt.x = self.left+20
        elif pack=='e':
            self.textbox.pt.x = self.right-20
        self.align_y = self.textbox.pt.y-20
        
class Panel(Box):
    def __init__(self,n_figures=1,*conversation):
        super().__init__()
        self.set_name("panel")
        self.figures = Array(n_figures, Stickfigure)
        self.bubbles
        for idx,figure in enumerate(self.figures):
            figure.floor = self.bottom.y - self.height/10
            figure.height = figure.width * 7/3
        padding = self.width*2/5 if n_figures==1 else self.width/8
        spacing = self.width/10
        for a,b in self.figures.adj_objs():
            b.left = a.right + spacing
            b.width = a.width
        self.figures[0].left = self.left.x + padding
        self.figures[-1].right = self.right.x - padding
        self.height = self.width
        if n_figures==1:
            self.speech = SpeechBubble(conversation[0])
            self.speech.headtop = self.figures[0].head.top
            self.speech.align_y = self.top.y + 20
        elif n_figures==2:
            self.speeches = InitorArray(SpeechBubble,*zip(conversation,"ww"))
            each(self.speeches).headtop = each(self.figures).head.top
            self.speeches[0].align_y = self.top.y + 20
            self.speeches[1].align_y = self.top.y + 60
            self.speeches[0].left = self.left.x + 20
            self.speeches[1].left = self.speeches[0].line.x + 20
            

# panel = Panel(2)
# panel.topleft = Point(padding,padding)
# panel.width = panel.height = 200
# print(panel.sim_draw())
# display(panel)

class Strip(Primitive):
    def __init__(self, N):
        self.panelwidth = 200
        step = 2
        self.panels = InitorArray(Panel,*zip(range(1,step*N+1,step)))
        self.topleft = self.panels.first.topleft = Point(padding,padding)
        for panel in self.panels:
            panel.width = self.panelwidth
        for a,b in self.panels.adj_objs():
            a.right = b.left

#display(Strip(1,300),w=400,h=300)
#print(Strip(1,300).sim_draw())
        
# display(Strip(3),w=650,h=250)

#strip = Strip(2)
#print(strip.sim_draw())
#display(strip,w=650,h=250)

panel1 = Panel(1,"Hello world!")
panel1.topleft = Point(padding,padding)
panel1.width = 200
panel2 = Panel(2,"Good morning!","Hello programs!")
panel2.topleft = Point(padding,padding) + Point(200,0)
display(panel1)