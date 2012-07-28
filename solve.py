from helpers import *

def solve_constraints(orig_constraints):
    constraints = orig_constraints.copy()
    variables = set().union( equ.variables() for equ in constraints )
    
    
def canonical_form(orig_constraints,variables):
    unused_constraints = list( orig_constraints )
    constraints = []
    for var in variables:
        for equ in unused_constraints:
            if equ.coefficient(var):
                break
        else:
            break
        unused_constraints.remove(equ)
        equ = normalised_constraint( equ, var)
        for idx in range(len(constraints)):
            constraints[idx] = reduce_constraint_by_equ_at_var(constraints[idx],equ,var)
        constraints.append(equ)
    return constraints

def normalised_constraint(equ, var):
    return equ / equ.coefficient(var)
    
def reduce_constraint_by_equ_at_var(constraint,equ,var):
    return constraint - constraint.coefficient(var) * equ
    