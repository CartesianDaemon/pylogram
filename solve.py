# Pylogram libraries
from helpers import *
from exceptions import *

def solve_constraints(orig_constraints, _=None, print_steps=ignore):
    var_constraints = variable_constraints( orig_constraints, variables(orig_constraints), print_steps )
    return { var : var_value(var,var_constraints[var]) if var in var_constraints else None for var in variables(orig_constraints) }
    
def var_value(var,equ):
    assert( equ.coefficient(var) == 1)
    return equ.solve_for_var(var) if equ.solvable() else None

def canonical_equs(orig_constraints,_=None):
    return list(variable_constraints(orig_constraints, variables(orig_constraints) ).values())
    
def variable_constraints(orig_constraints,variables, print_steps=ignore):
    unused_constraints = list( orig_constraints )
    constraints = {}
    print_steps("\n****************************************\n            Solving...\n*****************************************")
    print_steps("\nInput:")
    for orig_constraint in unused_constraints: print_steps(" >> ", orig_constraint)
    for var in variables:
        for equ in unused_constraints:
            if equ.coefficient(var):
                break
        else:
            # variable only appeared in constraints already used, ie. is defined non-uniquely in terms of a previous var
            print_steps("\nSkipping variable", var.name(), "...")
            continue
        print_steps("\nSolving for", var.name(), ":")
        unused_constraints.remove(equ)
        equ = normalised_constraint_for( equ, var)
        for prev_var, prev_constraint in constraints.items():
            constraints[prev_var] = reduce_constraint_by_equ_for_var(prev_constraint,equ,var)
            print_steps(" >> ", constraints[prev_var])
        for idx in range(len(unused_constraints)):
            unused_constraints[idx] = reduce_constraint_by_equ_for_var( unused_constraints[idx], equ, var)
            print_steps(" >> ", unused_constraints[idx])
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
    