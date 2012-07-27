# Usually import Var and Obj only

# Standard libraries
from numbers import Number
from collections import defaultdict

_next_var_idx = 0 # used for internal hashes, may remove later

class _Var:
    def __init__(self):
        global _next_var_idx
        self._idx = _next_var_idx
        _next_var_idx += 1

    def __hash__(self):
        return self._idx

    # def __getattr__(self, attr):
    #     if attr in ('__add__', '__mul__', '__radd__', '__rmul__', '__sub__', '__rsub__'):
    #         return lambda other: getattr( Expr(self), attr )( other )
    #     else:
    #         raise AttributeError

def Var():
    return Expr(_Var())
    
class Expr:
    def __init__(self, term):
        assert is_term( term )
        self._coeffs = defaultdict(int)
        self._add_term( term )

    def __hash__(self):
        return id(self)

    # def __eq__(self,other):
    #     assert is_term( other )
    #     return Equ( self, Expr(other) )
        
    def __add__(self,term):
        assert is_term( term )
        return self.copy()._add_term( term )

    def __mul__(self,term):
        assert is_term( term )
        return self.copy()._mul_term(term)
        
    def __sub__(self,term):
        assert is_term( term )
        return self + ( term * -1 )
        
    def __rsub__(self,term):
        assert is_term( term )
        return ( self * -1 ) + term
    
    def __radd__(self,term):
        assert is_term( term )
        return self + term
        
    def __rmul__(self,term):
        assert is_term( term )
        return self * term
        
    def copy(self):
        return Expr(self)

    def coefficients(self):
        return self._coeffs
        
    def variables(self):
        return set(self._coeffs.keys())

    def is_normalised(self):
        return all( (isinstance(var,Var) or var==1) and isinstance(coeff,Number) for var, coeff in self._coeffs.iteritems() )

    def _mul_term(self,term):
        assert isinstance(term, Number)
        assert self.is_normalised()
        for var in self._coeffs:
            self._coeffs[var] *= term;
        return self

    def _add_term(self, term, coeff=1):
        assert self.is_normalised()
        if isinstance(term, Number):
            self._coeffs[1] += term * coeff
        elif isinstance(term, Var):
            self._coeffs[term] += coeff
        elif isinstance(term,Expr):
            for subterm,subcoeff in term.coefficients().iteritems():
                self._add_term( subterm, subcoeff )
        return self

def is_term(term):
    return isinstance(term,Number) or isinstance(term,Var) or isinstance(term,Expr)
                
class Equ:
    def __init__( self, lhs, rhs ):
        assert isinstance(lhs, Expr)
        assert isinstance(rhs, Expr)
        self._expr_equals_zero = lhs - rhs
        
    def __nonzero__(self):
        # Only useful for making Vars compare equal to themself in a dict
        if all( coeff == 0 for coeff in _expr_equals_zero.values() ): return True
        return False
        
    def variables(self):
        return self._expr_equals_zero.variables()
        
    def coeffs_excluding_constant():
        return set( coeff for term, coeff in self._expr_equals_zero.coefficients() if isinstance(term,Number) and term == 1 )
        
    def rhs_constant():
        return -self._expr_equals_zero[1]

# TODO: Can we keep separate lists for each interconnected system of equations?

# Constraints represented as matrix: Ax=b
#
# A is n x m where n is number of variables and m is number of equations

class System:
    def __init__(self):
        self._constraints = []
        self._variables = set()
    
    # def constrain(self,equ):
    #     assert isinstance(equ, Equ)
    #     self._constraints.append(equ)
    #     self._variables |= equ.variables()

    def constrain_equals(self,lhs,rhs):
        assert isinstance(lhs, Expr)
        assert isinstance(rhs, Expr)
        equ = Equ(lhs,rhs)
        self._constraints.append(equ)
        self._variables |= equ.variables()
        
    def solved(self):
        return False
        
    def x(self):
        return tuple( self._variables )
        
    def A(self):
        pass
    
    def b(self):
        return ( equ.coefficients()[1] for equ in self._constraints )
        
    def solved_value(self,var):
        assert isinstance(var,Var)
        return None
    
class Obj:
    pass

