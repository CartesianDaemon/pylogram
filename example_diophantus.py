import pylogram

print("\nQ. Diophantus was a boy for one-sixth of his life. After one-twelfth more, he acquired a beard. After another one-seventh, he married. In the fifth year after his marriage his son was born. The son lived half as many as his father. Diophantus died 4 years after his son. How old was Diophantus when he died?\n")

age_at = pylogram.Varset()
age = age_at.death
sons_age = age_at.sons_death - age_at.sons_birth

age_at.adolescence [:]= age / 6
age_at.puberty     [:]= age_at.adolescence + age / 12
age_at.marriage    [:]= age_at.puberty + age / 7
age_at.sons_birth  [:]= age_at.marriage + 5
sons_age [:]= age / 2

print( " >>", age )

print("\nQ. OK, ok, if Diophantus also died 4 years after his son, how old was he when he died?\n")

age_at.death [:]= age_at.sons_death + 4

print( " >>", age )

# print( "\nQ. What about everything else?:\n" )
# 
# for var in pylogram.internals():
#     print( "  His age at", var.name(), "was", var.val() )