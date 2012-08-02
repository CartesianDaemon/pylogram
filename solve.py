# Pylogram libraries
from helpers import *
from exceptions import *

class Canonical:
    def __init__(self,orig_constraints, print_steps=ignore, undef=None):
        self._orig_constraints = orig_constraints
        self._print_steps = print_steps
        self._undef = undef
        self._variables = set()
        self._cncl_dict = {}
        self._var_values = defaultdict( lambda:self._undef )
        for new_constraint in orig_constraints:
            self.add_constraint(new_constraint)
        
    def var_value(self, var):
        return self._var_values.get( var, self._undef )
    
    def solved(self):
        return not self.free_vars()

    def variables(self):
        return self._variables
        
    def reduced_vars(self):
        return self._cncl_dict.keys()
        
    def free_vars(self):
        return self.variables() - self.reduced_vars()
    
    def values(self):
        return self._var_values.values()
    
    def __iter__(self):
        return iter(self.constraints())
    
    def constraints(self):
        return list(self._cncl_dict.values())
    
    def add_constraint(self, orig_new_constraint):
        print_steps = self._print_steps
        new_constraint = orig_new_constraint
        for var, equ in self._cncl_dict.items():
            new_constraint = new_constraint.reduce_by_equ_for_var(equ, var)
        assert not new_constraint.variables() & self.reduced_vars()
        if new_constraint.is_tautology():
            return
        if new_constraint.is_contradiction():
            raise Contradiction("New constraint",orig_new_constraint,"is reduced to contradiction",new_constraint)
        self._variables |= new_constraint.variables()
        new_var = first(new_constraint.variables())
        print_steps("\nSolving",new_constraint,"for", new_var.name(), ":")
        new_constraint = new_constraint.normalised_for(new_var)
        for var, constraint in self._cncl_dict.items():
            self._set_solved_constraint(var,constraint.reduce_by_equ_for_var(new_constraint,new_var))
        self._set_solved_constraint(new_var, new_constraint)

    def _set_solved_constraint(self, new_var, new_constraint):
        self._cncl_dict[new_var] = new_constraint
        self._var_values[new_var] = self._solve_var_value(new_var)
    
    def _solve_var_value(self, var):
        return self._cncl_dict[var].solve_for_var(var, undef=self._undef)
