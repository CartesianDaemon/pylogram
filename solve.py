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
            # variable only appeared in constraints already used, ie. is defined non-uniquely in terms of a previous var
            break
        unused_constraints.remove(equ)
        equ = normalised_constraint_for( equ, var)
        for idx in range(len(constraints)):
            constraints[idx] = reduce_constraint_by_equ_for_var(constraints[idx],equ,var)
        for idx in range(len(unused_constraints)):
            unused_constraints[idx] = reduce_constraint_by_equ_for_var( unused_constraints[idx], equ, var)
        constraints.append(equ)
    for equ in unused_constraints:
        if equ.is_null(): continue
        if equ.is_contradiction(): raise Contradiction
    return constraints

def normalised_constraint_for(equ, var):
    return equ / equ.coefficient(var)
    
def reduce_constraint_by_equ_for_var(constraint,equ,var):
    assert equ.coefficient(var)==1
    return constraint - constraint.coefficient(var) * equ
    