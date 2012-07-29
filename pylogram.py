# Usually import Var and Obj only

# Standard libraries
from numbers import Number
from fractions import Fraction

# Pylogram libraries
from helpers import *
from solve import solve_constraints
from exceptions import *

def is_var(val): return isinstance(val,Var)
def is_bare_term(val):return isinstance(val,Number) or isinstance(val,Var)
def is_term(val):return is_bare_term(val) or isinstance(val,Expr)
def is_expr(val): return isinstance(val,Expr)
def is_equ(val): return isinstance(val,EquZero)
def is_undef(val): return isinstance(val, _Undefined) 
def is_def(val): return not is_undef(val)
def is_num(term):  return isinstance(term,Number) # Any built-in constant type, eg. int, float or frac, but not Var instances
def is_evaluatable(term): return is_equ(term) or is_expr(term)

class Var:
    _next_var_idx = 0 # Used for debugging to make variables appear in hashes in expected order
    def __init__(self, name=None):
        self._name = name or "var_" + str(Var._next_var_idx)
        self._idx = Var._next_var_idx
        Var._next_var_idx +=1

    def __eq__      (self,other):  return Expr(self).__eq__     (other) # if not is_var(other) else id(self)==id(other)
    def __add__     (self,other):   return Expr(self).__add__    (other)
    def __mul__     (self,other):   return Expr(self).__mul__    (other)
    def __sub__     (self,other):   return Expr(self).__sub__    (other)
    def __rsub__    (self,other):   return Expr(self).__rsub__   (other)
    def __radd__    (self,other):   return Expr(self).__radd__   (other)
    def __rmul__    (self,other):   return Expr(self).__rmul__   (other)
    def __truediv__ (self,other):   return Expr(self).__truediv__(other)
    def __neg__     (self):        return Expr(self).__neg__()
    def __pos__     (self):        return Expr(self).__pos__()

    def __hash__(self):
        return self._idx

    def __repr__(self):
        return "Var('" + self._name + "')"

    def __str__(self):
        return self._name

    def name(self):
        return self._name
        
    def evaluate(self, system):
        return system._evaluate_var(self)

class Varset():
    def __init__(self):
        self._vars = {}

    def __getattr__(self,attr):
        # Doesn't apply to special attrs
        if attr in self._vars:
            return self._vars[attr]
        else:
            self._vars[attr] = Var(attr)
            return self._vars[attr]
    
    def __next__(self):
        # Allow tuple assignment. TODO: Should this be a separate function, not Varset?
        return Var()

class Expr:
    def __init__(self, term):
        assert is_term( term )
        self._coeffs = nonzero_dict()
        self._const = 0
        self._add_term( term )

    def __hash__(self):
        return id(self)

    def __eq__  (self,other):assert is_term(other); return EquZero( self - Expr(other) )
    def __add__ (self,term): assert is_term(term); return self.copy()._add_term( term )
    def __mul__ (self,term): assert is_term(term); return self.copy()._mul_term(term)
    def __sub__ (self,term): assert is_term(term); return self + -term
    def __rsub__(self,term): assert is_term(term); return -self + term
    def __radd__(self,term): assert is_term(term); return self + term
    def __rmul__(self,term): assert is_term(term); return self * term
    def __truediv__ (self,term): assert is_num(term); return self * Fraction(1,term)
    def __neg__(self): return -1 * self
    def __pos__(self): return 1 * self
    
    def var(self):
        assert(len(self._coeffs)==1)
        assert(self._const==0)
        return first(self._coeffs.keys())
    
    def copy(self):
        return Expr(self)

    def const(self):
        return self._const;
        
    def coefficient(self,variable):
        return self._coeffs[variable]

    def variables(self):
        return set(self._coeffs.keys())
        
    def is_tautologically_nonzero(self):
        return not self._coeffs and self._const != 0

    def is_tautologically_zero(self):
        return not self._coeffs and self._const == 0
        
    def is_unique(self):
        return len(self._coeffs)==1
        
    def is_normalised(self):
        assert is_num(self._const)
        return all( is_var(var) and is_num(coeff) for var,coeff in self._coeffs.items() )

    def _mul_term(self,term):
        assert is_num(term)
        val = term
        assert self.is_normalised()
        for var in self._coeffs:
            self._coeffs[var] *= val;
        self._const *= val
        return self

    def _add_term(self, term, coeff=1):
        assert self.is_normalised()
        if is_num(term):
            self._const += term * coeff
        elif is_var(term):
            self._coeffs[term] += coeff
        elif is_expr(term):
            for subterm,subcoeff in term._coeffs.items():
                self._add_term( subterm, subcoeff )
            self._const += term._const
        return self
        
    def evaluate(self, system):
        return self._const + sum( coeff * term.evaluate(system) for term,coeff in self._coeffs.items() )
        
    def is_def(self, system):
        return is_def( self.evaluate(system) )

    def __repr__(self):
        return " + ".join( repr(coeff) + "*" + repr(var) for var, coeff in self._coeffs.items() ) + " + " + str(self._const)
        
class EquZero:
    def __init__( self, lhs ):
        assert not is_equ(lhs)
        self._zero_expr = Expr(lhs)
        
    def __bool__(self):
        # TODO: Only checks for trivial cases, needed to check things like a==a in hashes
        # use system.evaluate() to check actual values
        return self.is_tautology()
    
    def __eq__(self,other): return is_equ(other) and self._zero_expr == other._zero_expr
    
    def __add__ (self, other): assert is_equ(other); return EquZero( self._zero_expr + other._zero_expr )
    def __sub__ (self, other): assert is_equ(other); return EquZero( self._zero_expr - other._zero_expr )
    def __mul__ (self, other): assert is_equ(other); return EquZero( self._zero_expr * other )
    def __rmul__(self, other): assert is_num(other); return EquZero( self._zero_expr * other )
    def __truediv__ (self, other): assert is_num(other); return EquZero( self._zero_expr / other )
    
    def is_tautology(self):
        return self._zero_expr.is_tautologically_zero()
    
    def is_contradiction(self):
        return self._zero_expr.is_tautologically_nonzero()
    
    def solvable(self):
        return self._zero_expr.is_unique()
        
    def solve_for_var(self, var):
        assert( self._zero_expr.variables() == {var} )
        return - self._zero_expr.const() / self._zero_expr.coefficient(var)
        
    def evaluate(self, system):
        val = self._zero_expr.evaluate(system)
        return (val) if is_undef(val) else (val==0)
        
    def is_def(self, system):
        return is_def( self.evaluate(system) )

    def copy(self):
        return EquZero(self._zero_expr.copy())
    
    def coefficient(self,variable):
        return self._zero_expr.coefficient(variable)
    
    def variables(self):
        return self._zero_expr.variables()
        
    def rhs_constant(self):
        return -self._zero_expr.const()
        
    def __repr__(self):
        return "{ " + repr(self._zero_expr) + " == 0 }"

def Equ(lhs,rhs):
    return EquZero(lhs-rhs)
        
class System:
    def __init__(self):
        self._constraints = []
        
    def try_constrain(self,equ):
        try:
            self.constrain(equ)
            return True
        except Contradiction:
            return False
    
    def constrain(self,equ):
        assert is_equ(equ)
        # Throw Contradiction if new constraint 
        self._constraints.append(equ)
        if equ.is_contradiction(): raise Contradiction
        self.test_for_contradictions()
        
    def test_for_contradictions(self):
        # self.solution() throws Contradiction if a conflicting constraint has been added
        self._solution()
        
    def solved(self):
        return not any( val is None for val in self.solution().values() )
    
    def variables(self):
        return set().union( * ( equ.variables() for equ in self._constraints ) )
    
    def evaluate(self,evaluand):
        if is_bare_term(evaluand):
            evaluand = Expr(evaluand)
        assert is_evaluatable(evaluand)
        if evaluand.is_def(self):
            return evaluand.evaluate(self)
        else:
            return 'undefined' # Or none
        
    def _solution(self):
        return solve_constraints(self._constraints,self.variables())
        
    def internals(self):
        return ( (var,self.evaluate(var)) for var in self.variables() )

    def _evaluate_var(self,var):
        if var not in self.variables(): raise NormaliseError
        return self._solution()[var] or _Undefined()

_default_system = System()

class _Undefined:
    def __add__ (self,other): return self
    def __radd__(self,other): return self
    def __sub__ (self,other): return self
    def __rsub__(self,other): return self
    def __mul__ (self,other): return 0 if other==0 else self
    def __rmul__(self,other): return 0 if other==0 else self

class Obj:
    pass
