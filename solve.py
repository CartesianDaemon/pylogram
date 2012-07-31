# Pylogram libraries
from helpers import *
from exceptions import *

class canonical:
    def __init__(self,orig_constraints, print_steps=ignore, undef=None):
        self._orig_constraints = orig_constraints
        self._print_steps = print_steps
        self._undef = undef
        self._variables = set()
        self._cncl_dict = {}
        self._var_values = defaultdict( lambda:self._undef )
        for new_constraint in orig_constraints:
            self.add_constraint(new_constraint)
        
    def var_values(self):
        return self._var_values
    
    def variables(self):
        return self._variables
        
    def reduced_vars(self):
        return self._cncl_dict.keys()
        
    def free_vars(self):
        return self.variables() - self.reduced_vars()
    
    def values(self):
        return self.var_values().values()
    
    def __iter__(self):
        return iter(self.constraints())
    
    def constraints(self):
        return list(self._cncl_dict.values())
    
    def add_constraint(self, new_constraint):
        print_steps = self._print_steps
        for var, equ in self._cncl_dict.items():
            new_constraint = reduce_constraint_by_equ_for_var( new_constraint, equ, var)
        new_vars = new_constraint.variables()
        assert not new_vars & self.reduced_vars()
        if new_constraint.is_tautology(): return
        if new_constraint.is_contradiction(): raise Contradiction
        self._variables |= new_vars
        new_var = first(new_vars)
        print_steps("\nSolving",new_constraint,"for", new_var.name(), ":")
        new_constraint = normalised_constraint_for( new_constraint, new_var)
        for var, constraint in self._cncl_dict.items():
            self._set_solved_constraint(var,reduce_constraint_by_equ_for_var(constraint,new_constraint,new_var))
        self._set_solved_constraint(new_var, new_constraint)

    def _set_solved_constraint(self, new_var, new_constraint):
        self._cncl_dict[new_var] = new_constraint
        self._var_values[new_var] = self._solve_var_value(new_var)
    
    def _solve_var_value(self, var):
        return self._cncl_dict[var].solve_for_var(var, undef=self._undef)
        
def normalised_constraint_for(equ, var):
    return equ / equ.coefficient(var)
    
def reduce_constraint_by_equ_for_var(constraint,equ,var):
    assert 1 == equ.coefficient(var)
    return constraint - constraint.coefficient(var) * equ
    