from pylogram import constrain, default_vars as vars

constrain(   vars.a + 5*vars.b == 22 , mod=17 )
constrain( 2*vars.a +   vars.b == -7 , mod=17 )

print( " >> a , b =", vars.a, ",", vars.b )

#  >> a , b = -23/5 , 33/5
