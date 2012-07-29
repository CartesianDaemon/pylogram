import pylogram

print("\nQ. Diophantus was a boy for one-sixth of his life. After one-twelfth more, he acquired a beard. After another one-seventh, he married. In the fifth year after his marriage his son was born. The son lived half as many as his father. Diophantus died 4 years after his son. How old was Diophantus when he died?\n")

system = pylogram.System()
age_at = pylogram.Varset()

system.constrain( age_at.death / 6 == age_at.adolescence )
system.constrain( age_at.puberty == age_at.adolescence + age_at.death / 12 )
system.constrain( age_at.marriage == age_at.puberty + age_at.death / 7 )
system.constrain( age_at.sons_birth == age_at.marriage + 5 )
system.constrain( age_at.death / 2  == age_at.sons_death - age_at.sons_birth )
system.constrain( age_at.death == age_at.sons_death + 4 )

print( "A. Diophantus died at age:", system.evaluate(age_at.death) )

print( "\nAnd in case you're curious\n" )

for var, val in system.internals():
    print( "  His age at", var, "was", val )