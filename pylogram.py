# Usually import Var and Obj only

# Standard libraries
from numbers import Number

# Pylogram libraries
from helpers import *

_next_var_idx = 0 # Used for debugging

class Contradiction(Exception):
    pass
    
class NormaliseError(Exception):
    pass

class _Var:
    def __init__(self):
        global _next_var_idx
        self._idx = _next_var_idx
        _next_var_idx += 1

    def __hash__(self):
        return self._idx
        
    def __repr__(self):
        return "var" + str(self._idx)
        
    def evaluate(self, system):
        return system._evaluate_var(self)

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
        self._coeffs = nonzero_dict()
        self._const = 0
        self._add_term( term )

    def __hash__(self):
        return id(self)

    def __eq__(self,other):
        assert is_term( other )
        return Equ( self, Expr(other) )

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

    def const(self):
        return self._const;
        
    def variables(self):
        return set(self._coeffs.keys())

    def is_null(self):
        if self._coeffs == {} and self._const == 0:
            return True
        elif self._coeffs == {} and self._const != 0:
            raise Contradiction
        else:
            return False
        
    def is_normalised(self):
        assert isinstance(self._const,Number)
        return all( isinstance(var,_Var) and isinstance(coeff,Number) for var,coeff in self._coeffs.iteritems() )

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
            for subterm,subcoeff in term._coeffs.iteritems():
                self._add_term( subterm, subcoeff )
            self._const += term._const
        return self
        
    def evaluate(self, system):
        return self._const + sum( coeff * term.evaluate(system) for term,coeff in self._coeffs.iteritems() )
        
    def __repr__(self):
        return "<Expr " + repr(self._coeffs) + " + " + str(self._const) + ">"

def is_term(term):
    return isinstance(term,Number) or isinstance(term,_Var) or isinstance(term,Expr)
                
class Equ:
    def __init__( self, lhs, rhs ):
        self._expr_equals_zero = Expr(lhs) - Expr(rhs)
        
    def __nonzero__(self):
        # TODO: Only checks for trivial cases, needed to check things like a==a in hashes
        # need to evaluate variables to check real values
        return self._expr_equals_zero.is_null()
        
    def variables(self):
        return self._expr_equals_zero.variables()
        
    def rhs_constant(self):
        return -self._expr_equals_zero.const()

# TODO: Can we keep separate lists for each interconnected system of equations?

# Constraints represented as matrix: Ax=b
#
# A is n x m where n is number of variables and m is number of equations

class System:
    def __init__(self):
        self._constraints = []
        self._variables = set()
    
    def constrain(self,equ):
        assert isinstance(equ, Equ)
        self._constraints.append(equ)
        self._variables |= equ.variables()

    def constrain_equals(self,lhs,rhs):
        self.constrain( Equ(lhs,rhs) )

    def constrain_zero(self,lhs):
        self.constrain( Equ(lhs,0))
        
    def solved(self):
        return False
    
    def variables(self):
        return self._variables
    
    def x(self):
        return tuple( Expr(var) for var in self._variables )
        
    def A(self):
        pass
    
    def b(self):
        return tuple( equ.rhs_constant() for equ in self._constraints )
        
    def evaluate(self,expr):
        assert is_term(expr)
        val = Expr(expr).evaluate(self)
        return None if isinstance(val, _Undefined) else val
        
    def _evaluate_var(self,var):
        if var not in self.variables():
            raise NormaliseError
        else:
            # TODO: do matrix inversion, return value or _Undefined() if unconstrained
            return _Undefined()

class _Undefined:
    def __getattr__(self,attr):
        if attr in ('__add__', '__mul__', '__radd__', '__rmul__', '__sub__', '__rsub__'):
            return lambda other: self.do_op(attr,other)
        else:
            raise AttributeError

    def do_op(self,attr,other):
        assert attr in ('__add__', '__mul__', '__radd__', '__rmul__', '__sub__', '__rsub__')
        if (attr=='__mul__' or attr=='__rmul__') and other==0:
            return lambda other: 0
        else:
            return self

class Obj:
    pass
