from helpers import *

def solve_constraints(orig_constraints):
    constraints = orig_constraints.copy()
    variables = set().union( equ.variables() for equ in constraints )
    
    
def canonical_form(orig_constraints,variables):
    unused_constraints = list( orig_constraints )
    constraints = []
    for var in variables:
        for equ in unused_constraints:
            if equ.coefficient(var):break
        unused_constraints.remove(var)
        equ = equ / equ.coefficient(var)
        #for constraints
    return constraints