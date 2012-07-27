
class Num:
    def constrain(self, other):
        self._constraints.append(other)

class Object:
    pass
    

a = Num()
b = Num()

a.constrain( b * 2 )

print a