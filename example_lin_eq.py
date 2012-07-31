from pylogram import constrain, default_vars as vars

constrain(   vars.a + vars.b   == 2  ,
           2*vars.a + vars.b/3 == -7 )

print( " >> a , b =", vars.a, ",", vars.b )

#  >> a , b = -23/5 , 33/5
