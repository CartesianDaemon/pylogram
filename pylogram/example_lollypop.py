from draw import *
 
class Lollypop(Primitive):
    def __init__(self):
        self.stick = Line('stick')
        self.circ = Circle('ball')
        self.circ.bottom = self.stick.pt1
        self.stick.pt1.x = self.stick.pt2.x
        line_height = self.stick.pt2.y - self.stick.pt1.y
        line_height [:]= self.circ.d * 2
        self.bottom = self.stick.pt2
        self.height = line_height + self.circ.d
        self.mid = self.circ.bottom

small_lollypop = Lollypop()
small_lollypop.bottom = Point(1,0)
small_lollypop.height = 6

big_lollypop = Lollypop()
big_lollypop.mid = Point(150,150)
big_lollypop.height = 150

# Example of deducing coordinates

assert small_lollypop.circ.c == Point(1,-5)

# Example of drawing to screen

display( big_lollypop )

# Look at how drawing happens

print(big_lollypop.sim_draw())

