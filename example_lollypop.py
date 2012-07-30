from pylogram_draw import *
 
class Lollypop(Obj):
    def __init__(self):
        self.stick = Line('stick')
        self.circ = Circle('ball')
        self.circ.bottom = self.stick.pt1
        self.stick.pt1.x = self.stick.pt2.x
        line_height = self.stick.pt2.y - self.stick.pt1.y
        line_height [:]= self.circ.d * 2
        self.bottom = self.stick.pt2
        self.height = line_height + self.circ.d

lollypop = Lollypop()
lollypop.bottom = Point(1,0)
lollypop.height = 6

assert lollypop.circ.c == Point(1,-5)

print(lollypop.sim_draw())

#  >> Drawing circle about 1,-5 with radius 1
#  >> Drawing line from 1,-4 to 1,0

# Not implemented yet:

# lollypop.draw()
