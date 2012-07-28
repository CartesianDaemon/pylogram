# Pylogram libraries
from helpers import *
from exceptions import *

def solve_constraints(orig_constraints, variables):
    constrained_vars = constrained_variables( orig_constraints, variables )
    return { var : var_value(var,constrained_vars[var]) if var in constrained_vars else None for var in variables }
    
def var_value(var,equ):
    assert( equ.coefficient(var) == 1)
    return equ.solve_for_var(var) if equ.solvable() else None

def canonical_equs(orig_constraints,variables):
    return list(constrained_variables(orig_constraints,variables).values())
    
def constrained_variables(orig_constraints,variables):
    unused_constraints = list( orig_constraints )
    constraints = {}
    for var in variables:
        for equ in unused_constraints:
            if equ.coefficient(var):
                break
        else:
            # variable only appeared in constraints already used, ie. is defined non-uniquely in terms of a previous var
            continue
        unused_constraints.remove(equ)
        equ = normalised_constraint_for( equ, var)
        for prev_var, prev_constraint in constraints.items():
            constraints[prev_var] = reduce_constraint_by_equ_for_var(prev_constraint,equ,var)
        for idx in range(len(unused_constraints)):
            unused_constraints[idx] = reduce_constraint_by_equ_for_var( unused_constraints[idx], equ, var)
        constraints[var] = equ
    for equ in unused_constraints:
        if equ.is_tautology(): continue
        if equ.is_contradiction(): raise Contradiction
        print(equ)
        raise AssertionError # Should never get here
    return constraints

def normalised_constraint_for(equ, var):
    return equ / equ.coefficient(var)
    
def reduce_constraint_by_equ_for_var(constraint,equ,var):
    assert equ.coefficient(var)==1
    return constraint - constraint.coefficient(var) * equ
    