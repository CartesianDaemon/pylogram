# Usually import Var and Obj only

# Standard libraries
from numbers import Number
from fractions import Fraction

# Pylogram libraries
from helpers import *
from solve import solve_constraints
from exceptions import *

# WARNING: Changed to primarily use global a[:]=b instead of system.constrain( a==b )
# If you use system.constrain( a==b ) and then to print(a) not print(system.evaluate(a)) you will get weird results
# Systems may eventually be deprecated, or changed to only work with "with"

def is_var(val): return isinstance(val,Var)
def is_bare_term(val):return isinstance(val,Number) or isinstance(val,Var)
def is_term(val):return is_bare_term(val) or isinstance(val,Expr)
def is_expr(val): return isinstance(val,Expr)
def is_equ(val): return isinstance(val,EquZero)
def is_undef(val): return isinstance(val, _Undefined) # Works on evaluations, not expr. TODO: Change this?
def is_def(val): return not is_undef(val)
def is_num(term):  return isinstance(term,Number) # Any built-in constant type, eg. int, float or frac, but not Var instances
def is_evaluatable(term): return is_equ(term) or is_expr(term)
def is_frac(term): return isinstance(term,Fraction)

class Var:
    _next_var_idx = 0 # Used for debugging to make variables appear in hashes in expected order
    def __init__(self, name=None):
        self._name = name or "var_" + str(Var._next_var_idx)
        self._idx = Var._next_var_idx
        Var._next_var_idx +=1
        self._cached_val_str = "" # Used for debug repr only

    def __eq__      (self,other):  return Expr(self).__eq__     (other) # if not is_var(other) else id(self)==id(other)
    def __setitem__ (self,pos,val):return Expr(self).__setitem__(pos,val)
    def constrain   (self,rhs):    return Expr(self).constrain  (rhs)
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
        # avoid calculating answer here
        return "Var<" + self._name + "=" +self._cached_val_str + ">" 

    def __str__(self):
        return str(self.val())

    def name_or_value(self, system=None):
        return str(self.val(system)) if self.is_def(system) else self.name()
        
    def name(self):
        return self._name
        
    def is_def(self, system = None ):
        return is_def(self.evaluate(system))

    def val(self,system = None): # Only meaningful is assigned with module-level constrain() or [:]=
        return self.evaluate(system)
        
    def evaluate(self, system = None):
        if system is None: system = default_sys()
        if system is default_sys(): self._cached_val_str = str( system._evaluate_var(self) )
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
    
    def make(self):
        var = Var()
        setattr(self, var.name(), var)
        return var
    
    def make_n(self, n):
        class var_iter:
            def __init__(self, varset):
                self._varset, self._n = varset, n
            def __iter__(self):
                return self
            def __next__(self):
                if self._n<=0: raise StopIteration
                self._n -=1;
                return self._varset.make()
        return var_iter(self)

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
    
    def __setitem__(self, emptyslice, rhs):
        # Support "a [:]= b" syntax
        assert emptyslice == slice(None, None, None)
        self.constrain(rhs)
    
    def constrain(self, rhs):
        default_sys().constrain( Equ( self, rhs ) )
        
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
        
    def is_nonnull(self):
        return not self._coeffs and self._const != 0

    def is_null(self):
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

    def _format_frac(self, frac, var_name = None):
        return self._format_num(frac.numerator, var_name) + "/" + str(frac.denominator)
        
    def _form_num_with_sign(self,coeff):
        spc = " "
        return ( "+" if coeff>=0 else "-" ) + spc + str(abs(coeff))

    def _format_num(self, coeff, var_name = None):
        spc = " "
        mul="."
        if is_frac(coeff):
            return self._format_frac(coeff, var_name)  if var_name or coeff else '' 
        elif var_name:
            return ( "-"+spc if coeff==-1 else "+"+spc if coeff==1 else self._form_num_with_sign(coeff)+mul ) + var_name
        else:
            return self._form_num_with_sign(coeff) if coeff else '' 
        
    def __repr__(self):
        spc = " "
        coeff_reprs = [ self._format_num(coeff,var.name()) for var,coeff in self._coeffs.items() ]
        coeff_reprs.append( self._format_num(self._const) )
        str = spc.join( coeff_reprs )
        return ("-" if str[0]=='-' else "") + str.strip('+ -')
        
class EquZero:
    def __init__( self, lhs ):
        assert not is_equ(lhs)
        self._zero_expr = Expr(lhs)
        
    def __bool__(self):
        # For constraints applied to the global default system eg. "a[:]=2", can be used directly eg. "a==2" is True
        # For constraints applied to a specific system eg. "sys.constrain(a*2==2)", only checks for tautology, eg. "a==a" is True
        # but "a==b" is false regardless of the values of a and b in sys. To compare actual values, use sys.evaluate(a==1)
        if self.is_tautology():
            return True
        elif self.is_contradiction():
            return False
        else:
            return self._zero_expr.variables() < default_sys().variables() and default_sys().evaluate(self)
    
    def __add__ (self, other): assert is_equ(other); return EquZero( self._zero_expr + other._zero_expr )
    def __sub__ (self, other): assert is_equ(other); return EquZero( self._zero_expr - other._zero_expr )
    def __mul__ (self, other): assert is_equ(other); return EquZero( self._zero_expr * other )
    def __rmul__(self, other): assert is_num(other); return EquZero( self._zero_expr * other )
    def __truediv__ (self, other): assert is_num(other); return EquZero( self._zero_expr / other )
    
    def __eq__(self,other):
        # Test for equivalance between equations,
        # ie. (a==2) == (a==2) regardless of which systems a is defined in but (a==2) != (-a==-2)
        # Used list.remove(equ) and in [equ1, equ2] == [equ1, equ2]
        return is_equ(other) and self._zero_expr == other._zero_expr
    
    def is_tautology(self):
        return self._zero_expr.is_null()
    
    def is_contradiction(self):
        return self._zero_expr.is_nonnull()
    
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
        return "{ 0 = " + repr(self._zero_expr) + " }"

def Equ(lhs,rhs):
    return EquZero(lhs-rhs)

class System:
    def __init__(self, *constraints):
        self._constraints = list(constraints)
        
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
        
    def constraints(self):
        return self._constraints
        
    def test_for_contradictions(self):
        # self.solution() throws Contradiction if a conflicting constraint has been added
        self._solution()
        
    def solved(self):
        return not any( val is None for val in self._solution().values() )
    
    def variables(self):
        return variables(self._constraints)
    
    def evaluate(self,evaluand):
        if is_bare_term(evaluand):
            evaluand = Expr(evaluand)
        return evaluand.evaluate(self)
        # if evaluand.is_def(self):
        #     return evaluand.evaluate(self)
        # else:
        #     return undefined()
            
    def _solution(self):
        return solve_constraints(self._constraints, print_steps = _solve_debug_print)
        
    def internals(self):
        return ( (var,self.evaluate(var)) for var in variables( self._constraints ) )

    def _evaluate_var(self,var):
        return var in self.variables() and self._solution()[var] or _Undefined()

def undefined():
    # Note: _Undefined used internally, but we return None or 'undefined' so caller can do "if aa == 'undefined'"
    return 'undefined'
    # return None
        
_default_sys = System()
_solve_debug_print = ignore # Used for debugging

def default_sys(): return _default_sys

# Only use these outside the module, inside use _default_sys.blah() or default_sys().blah() directly

def constrain(equ): return default_sys().constrain( equ )
def evaluate(e):    return default_sys().evaluate( e )
def internals(e):   return default_sys().internals( e )

def reset_internals():
    # Used for testing systemwide constraints multiple times
    global _default_sys
    global _solve_debug_print
    _default_sys = System()
    Var._next_var_idx = 0
    _solve_debug_print = ignore
    
class _Undefined:
    def __eq__  (self,other): return other==undefined() # Not equal to self
    def __add__ (self,other): return self
    def __radd__(self,other): return self
    def __sub__ (self,other): return self
    def __rsub__(self,other): return self
    def __mul__ (self,other): return 0 if other==0 else self
    def __rmul__(self,other): return 0 if other==0 else self
    def __repr__(self): return "_Undefined"
    def __str__(self): return str(undefined())

class Obj:
    pass
