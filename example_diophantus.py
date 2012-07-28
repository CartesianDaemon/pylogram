import pylogram

# He was a boy for one-sixth of his life. After one-twelfth more, he acquired a beard. After another one-seventh, he married. In the fifth year after his marriage his son was born. The son lived half as many as his father. Diophantus died 4 years after his son. How old was Diophantus when he died?

# TODO: Shorter syntax for declaring many variables
birth      = pylogram.Var()
eo_boyhood = pylogram.Var()
beard      = pylogram.Var()
marriage   = pylogram.Var()
son        = pylogram.Var()
son_dies   = pylogram.Var()
death      = pylogram.Var()
life       = pylogram.Var()

system = pylogram.System()

system.constrain( eo_boyhood - birth == life / 6  )
system.constrain( beard == eo_boyhood + life / 12 )
system.constrain( marriage == beard + life / 7    )
system.constrain( son == marriage + 5             )
system.constrain( (son_dies - son) == life / 2    )
system.constrain( death == son_dies + 4           )
system.constrain( life == death - birth           )

print( system.evaluate( life ) )
