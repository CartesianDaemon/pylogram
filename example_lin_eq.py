import pylogram

vars = pylogram.Varset()

eq1 =    vars.a + vars.b   == 2
eq2 =  2*vars.a + vars.b/3 == -7

test =  5*vars.a +23 == 0
#assert not test.evaluate(test)

pylogram.constrain( eq1, eq2 )

#assert test.evaluate(test)
print( "a , b =", vars.a, ",", vars.b )