from pylogram import constrain, vars

constrain(   vars.a + vars.b   == 2
constrain( 2*vars.a + vars.b/3 == -7

print( "a , b =", vars.a, ",", vars.b )