# Usually import Var and Obj only

# Standard libraries
from numbers import Number

# Pylogram libraries
from helpers import *
from solve import solve_constraints
from exceptions import *

_next_var_idx = 0 # Used for debugging to make variables appear in hashes in expected order

class _Var:
    def __init__(self, name, idx):
        self._name = name
        self._idx = idx

    def __hash__(self):
        return self._idx
        
    def __repr__(self):
        return "Var('" + self._name + "')"
        
    def __str__(self):
        return self._name
        
    def evaluate(self, system):
        return system._evaluate_var(self)

def Var(orig_name = None):
    global _next_var_idx
    var = _Var( name = orig_name if orig_name else "var_" + str(_next_var_idx), idx=_next_var_idx )
    _next_var_idx += 1
    return Expr(var)

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
    def __neg__(self): return -1 * self
    def __pos__(self): return 1 * self
    def __truediv__ (self,term): assert is_num(term); return self * (1/term)
    
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
        assert isinstance(self._const,Number)
        return all( isinstance(var,_Var) and isinstance(coeff,Number) for var,coeff in self._coeffs.items() )

    def _mul_term(self,term):
        assert isinstance(term, Number)
        val = term
        assert self.is_normalised()
        for var in self._coeffs:
            self._coeffs[var] *= val;
        self._const *= val
        return self

    def _add_term(self, term, coeff=1):
        assert self.is_normalised()
        if isinstance(term, Number):
            self._const += term * coeff
        elif isinstance(term, _Var):
            self._coeffs[term] += coeff
        elif isinstance(term,Expr):
            for subterm,subcoeff in term._coeffs.items():
                self._add_term( subterm, subcoeff )
            self._const += term._const
        return self
        
    def evaluate(self, system):
        return self._const + sum( coeff * term.evaluate(system) for term,coeff in self._coeffs.items() )
        
    def __repr__(self):
        return " + ".join( repr(coeff) + "*" + repr(var) for var, coeff in self._coeffs.items() ) + " + " + str(self._const)

def is_term(val):
    return isinstance(val,Number) or isinstance(val,_Var) or isinstance(val,Expr)

def is_equ(val):
    return isinstance(val,EquZero)

def is_undef(val):
    return isinstance(val, _Undefined) 
    
def is_def(val):
    return not is_undef(val)

class EquZero:
    def __init__( self, lhs ):
        if isinstance(lhs,EquZero):
            assert False
        self._zero_expr = Expr(lhs)
        
    def __bool__(self):
        # TODO: Only checks for trivial cases, needed to check things like a==a in hashes
        # use system.evaluate() to check actual values
        return self.is_tautology()
    
    def __eq__(self,other): return isinstance(other,EquZero) and self._zero_expr == other._zero_expr
    
    def __add__ (self, other): assert isinstance(other,EquZero); return EquZero( self._zero_expr + other._zero_expr )
    def __sub__ (self, other): assert isinstance(other,EquZero); return EquZero( self._zero_expr - other._zero_expr )
    def __mul__ (self, other): assert isinstance(other,Number); return EquZero( self._zero_expr * other )
    def __rmul__(self, other): assert isinstance(other,Number); return EquZero( self._zero_expr * other )
    def __truediv__ (self, other): assert isinstance(other,Number); return EquZero( self._zero_expr / other )
    
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
        
# TODO: Can we keep separate lists for each interconnected system of equations?

# Constraints represented as matrix: Ax=b
#
# A is n x m where n is number of variables and m is number of equations

class System:
    def __init__(self):
        self._constraints = []
    
    def constrain(self,equ):
        assert isinstance(equ, EquZero)
        self._constraints.append(equ)
        # TODO: Change this...
        if equ.is_contradiction(): raise Contradiction
        # ... to calling solve.solve_constraints and ignoring result.

    def constrain_equals(self,lhs,rhs):
        self.constrain( EquZero(lhs-rhs) )

    def constrain_zero(self,lhs):
        self.constrain( EquZero(lhs) )
        
    def solved(self):
        return all( val is not None for val in solve_matrix( self.A(), self.b() ) )
    
    def variables(self):
        return set().union( * ( equ.variables() for equ in self._constraints ) )
    
    def x(self):
        return tuple( Expr(var) for var in self.variables() )
        
    def A(self):
        return tuple( tuple( equ.coefficient(var) for var in self.variables() ) for equ in self._constraints )
    
    def b(self):
        return tuple( equ.rhs_constant() for equ in self._constraints )
        
    def evaluate(self,expr):
        assert is_term(expr) or is_equ(expr)
        if is_equ(expr):
            val = expr.evaluate(self)
        else:
            val = Expr(expr).evaluate(self)
        return val if is_def(val) else None

    def variable_values(self):
        return solve_matrix( self.A(), self.b() )

    def variable_dict(self):
        #assert len(self.variables())==len(self.variable_values())
        # return dict( zip( self.variables(), self.variable_values() ) )
        return solve_constraints( self._constraints, self.variables() )

    def _evaluate_var(self,var):
        if var not in self.variables():
            raise NormaliseError
        else:
            return self.variable_dict()[var] or _Undefined()

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
