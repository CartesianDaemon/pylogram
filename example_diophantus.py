import pylogram

print "It is said of Diophantus that he was a boy for one-sixth of his life. After one-twelfth more, he acquired a beard. After another one-seventh, he married. In the fifth year after his marriage his son was born. The son lived half as many as his father. Diophantus died 4 years after his son. How old was Diophantus when he died?\n\n"

# TODO: Shorter syntax for declaring many variables
date_of_birth      = pylogram.Var('date_of_birth'     )
date_of_adolescence= pylogram.Var('date_of_adolescence')
date_of_beard      = pylogram.Var('date_of_beard'     )
date_of_marriage   = pylogram.Var('date_of_marriage'  )
date_of_sons_birth = pylogram.Var('date_of_sons_birth'       )
date_of_sons_death = pylogram.Var('date_of_sons_death'  )
date_of_death      = pylogram.Var('date_of_death'     )
age                = pylogram.Var('age'      )

system = pylogram.System()

system.constrain( date_of_adolescence - date_of_birth == age / 6  )
system.constrain( date_of_beard == date_of_adolescence + age / 12 )
system.constrain( date_of_marriage == date_of_beard + age / 7    )
system.constrain( date_of_sons_birth == date_of_marriage + 5             )
system.constrain( (date_of_sons_death - date_of_sons_birth) == age / 2    )
system.constrain( date_of_death == date_of_sons_death + 4           )
system.constrain( age == date_of_death - date_of_birth           )

print( "Diophantus died at age: ".format( system.evaluate( age ) ) )
