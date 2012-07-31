from pylogram_draw import *

padding = 25

class Panel(Square):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.topleft = Point(padding,padding)
        
class Strip(Array):
    def __init__(self, N, width = 100):
        super().__init__(N,Panel)
        for a,b in self.adj_objs():
            a.right.x = b.left.x
            print(pyl.constraints())
        # constrain( self._arr[0].width * N == width )

print(Strip(3,200).sim_draw())
        
# display(Strip(3,200),w=650,h=250)
# 
# display(Strip(5,100),w=550,h=150)
