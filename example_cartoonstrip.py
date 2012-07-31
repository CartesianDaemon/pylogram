from pylogram_draw import *

padding = 25

class Panel(Box):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
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

display(Strip(1,300),w=400,h=300)
print(Strip(1,300).sim_draw())
        
# display(Strip(3,600, 200),w=650,h=250)
# 
# display(Strip(5,600),w=650,h=150)
