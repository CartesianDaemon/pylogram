# TODO: Derive from appropriate exceptions

class PylogramError(Exception):
    pass

# Raised when contradictory constraints are required.
# equ = var + 1 == var + 2 # <-- evals false, no exception
# constrain(equ) # <-- exception
# Should be raised if new constraint conflicts with any
# in the same system.
# May sometimes get this exception later?
class Contradiction(PylogramError):
    pass
    
# If you multiply or divide two linear variables, the
# result is unsolvable and a PolynomialError is raised
class PolynomialError(PylogramError):
    pass
    