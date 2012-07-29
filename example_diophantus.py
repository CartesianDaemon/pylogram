import pylogram

print("\nQ. Diophantus was a boy for one-sixth of his life. After one-twelfth more, he acquired a beard. After another one-seventh, he married. In the fifth year after his marriage his son was born. The son lived half as many as his father. Diophantus died 4 years after his son. How old was Diophantus when he died?\n")

age_at = pylogram.Varset()
age = pylogram.Varset().age
sons_age = pylogram.Varset().sons_age

age [:]= age_at.death
age_at.adolescence [:]= age / 6
age_at.puberty [:]= age_at.adolescence + age / 12
age_at.marriage [:]= age_at.puberty + age / 7
age_at.sons_birth [:]= age_at.marriage + 5
sons_age [:]= age_at.sons_death - age_at.sons_birth
sons_age [:]= age / 2

# print( "A. Diophantus died at age:", age )
# 
# print("\nQ. OK, OK, if Diophantus also died 4 years after his son, how old was he when he died?\n")

age_at.death [:]= age_at.sons_death + 4

print( "A. Diophantus died at age:", age )

print( "\nAnd in case you're curious, the internal workings were:\n" )

for var, val in system.internals():
    print( "  His age at", var, "was", val )