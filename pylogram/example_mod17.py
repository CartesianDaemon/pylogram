from pylogram import constrain, default_vars as vars

constrain(   vars.a + 5*vars.b == 22 , mod=17 )
constrain( 2*vars.a +   vars.b == -5 , mod=17 )

print( " >> a , b =", vars.a, ",", vars.b )

#  >> a , b = 8, 13

assert (   8 + 5*13)%17 , (22)%17
assert ( 2*8 +   13)%17 , (-6)%17

