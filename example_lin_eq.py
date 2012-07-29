import pylogram

vars = pylogram.Varset()

eq1 =    vars.a + vars.b   == 2
eq2 =  2*vars.a + vars.b/3 == -7

pylogram.constrain( eq1, eq2 )

print( "a , b =", vars.a, ",", vars.b )