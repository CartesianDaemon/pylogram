from __future__ import division
# Standard libraries
from numbers import Number
from fractions import Fraction

# Pylogram libraries
from helpers import *
from solve import Canonical
from excpt import *

# WARNING: Changed to primarily use global a[:]=b instead of system.constrain( a==b )
# If you use system.constrain( a==b ) and then to print(a) not print(system.evaluate(a)) you will get weird results
# Systems may eventually be deprecated, or changed to only work with "with"

# Possible syntaxes (will be simplified):
#
# constrain( a==2*b )    # clear, but I hate the superfluous bracket at the right
# a [:]= 2*b             # too cute, but precedence is bad if a becomes a * b as [:]= applies to b only
# let| a==2*b            # ????
# a ~ b                  # If this were "=" I'd be happy, but it's not clear enough this is DOING something
# obj.a = obj.b          # In obj setattr function. Weird, but beautiful if we're happy to always be members of objects

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
def is_bool(val): return isinstance(val,bool)

class Var:
    _next_var_idx = 0 # Used for debugging to make variables appear in hashes in expected order
    def __init__(self, name=None, prefer=Fraction):
        self._idx = Var._next_var_idx
        self._name = name or "var_" + str(self._idx)
        self._is_anon = name is None
        Var._next_var_idx +=1
        self._cached_val = { default_sys() : "" } # Used for debug repr only
        self._prefer_type = prefer
        
    # Normally only used immediately after __init__
    def set_name(self, name=None):
        self._name = name or "var_" + str(Var._next_var_idx)
        self._is_anon = False

    def is_anon(self):
        return self._is_anon

    def __eq__         (self,other):  return Expr(self).__eq__           (other) # if not is_var(other) else id(self)==id(other)
    def __setitem__    (self,pos,val):return Expr(self).__setitem__      (pos,val)
    def constrain_equal(self,rhs):    return Expr(self).constrain_equal  (rhs)
    def __add__        (self,other):   return Expr(self).__add__    (other)
    def __mul__        (self,other):   return Expr(self).__mul__    (other)
    def __sub__        (self,other):   return Expr(self).__sub__    (other)
    def __rsub__       (self,other):   return Expr(self).__rsub__   (other)
    def __radd__       (self,other):   return Expr(self).__radd__   (other)
    def __rmul__       (self,other):   return Expr(self).__rmul__   (other)
    def __truediv__    (self,other):   return Expr(self).__truediv__(other)
    def __div__        (self,other):   return Expr(self).__div__(other)
    def __neg__        (self):        return Expr(self).__neg__()
    def __pos__        (self):        return Expr(self).__pos__()

    def __hash__(self):
        return self._idx

    def __repr__(self):
        # avoid calculating answer here
        return "Var<" + self._name + "=" +str(self._cached_val[default_sys()]) + ">" 

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
        if system is None:
            system = default_sys()
        self._cached_val[system] = system.evaluate(self)
        return self._cached_val[system]

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
            def next(self):
                return self.__next__()
            def __next__(self):
                if self._n<=0: raise StopIteration
                self._n -=1;
                return self._varset.make()
        return var_iter(self)

class Expr:
    def __init__(self, term=None, _init_coeff_vars = {}, _init_const = 0, mod=None):
        self._make_from(_init_coeff_vars,_init_const,mod)
        if term is not None:
            assert is_term( term )
            self._add_term( term )
        self._normalise_self()

    def _make_from(self,coeff_vars,const,mod):
        self._coeffs = nonzero_dict(coeff_vars, delta=0.001)
        self._const = const
        self._mod = mod
        return self
        
    def set_coeff(self,var,coeff):
        self._coeffs[var] = coeff
        return self

    def mod(self,n):
        return Expr(_init_coeff_vars=self._coeffs, _init_const=self._const, mod = n)
    
    def copy(self):
        return Expr(_init_coeff_vars=self._coeffs, _init_const=self._const, mod = self._mod)

    def normalised_for(self,n_var):
        inv = self._inverse(self.coefficient(n_var), self._mod)
        init_coeff_vars = { var : (1 if var is n_var else coeff*inv) for var,coeff in self._coeffs.items() }
        return Expr( _init_coeff_vars=init_coeff_vars, _init_const= self._const * inv, mod= self._mod) 

    def minus_excluding(self,exclude_var):
        return Expr( _init_coeff_vars={ var:-coeff for var,coeff in self._coeffs if var is not exclude_var.items() }, _init_const=-self._const , mod = self._mod)

    def __hash__(self):
        return id(self)

    def __eq__  (self,other):
        if is_term(other):
            return EquZero( self - Expr(other) )
        elif other==undefined():
            return self.is_undef()
        else:
            return False

    def __add__ (self,term): assert is_term(term); return self.copy()._add_term( term )
    def __mul__ (self,term): assert is_term(term); return self.copy()._mul_term(term)
    def __truediv__ (self,term): assert is_num(term); return self.copy()._mul_term(self._inverse(term))
    def __div__ (self,term): return self.__truediv__(term)
    def __sub__ (self,term): assert is_term(term); return self + -term
    def __rsub__(self,term): assert is_term(term); return -self + term
    def __radd__(self,term): assert is_term(term); return self + term
    def __rmul__(self,term): assert is_term(term); return self * term
    def __neg__(self): return -1 * self
    def __pos__(self): return 1 * self
    
    def _inverse(self,val, mod = None):
        assert mod == self._mod
        if self._mod is not None:
            return inverse_mod_n(val,self._mod)
        else:
            prefer_type = first( ( var._prefer_type for var in self.variables()), (type(self._const),) )
            return prefer_type(1)/val

    def __setitem__(self, emptyslice, rhs):
        # Support "a [:]= b" syntax
        # assert emptyslice == slice(None, None, None)
        self.constrain_equal(rhs)
        return Equ(self,rhs)
    
    def constrain_equal(self, rhs):
        default_sys().constrain( Equ( self, rhs ) )
        
    def var(self):
        assert(len(self._coeffs)==1)
        assert(self._const==0)
        return first(self._coeffs.keys())
    
    def _normalise_self(self):
        if self._mod is not None:
            for var,coeff in self._coeffs.items():
                self._coeffs[var] = mod_n(coeff, self._mod)
            self._const = mod_n(self._const,self._mod)
        return self
    
    def normalised(self,mod):
        assert mod==self._mod
        return self.copy().mod(mod)._normalise_self()

    def const(self):
        return self._const;
        
    def coefficient(self,variable):
        return self._coeffs[variable]

    def variables(self):
        return set(self._coeffs.keys())
        
    def is_nonnull(self):
        return not self._coeffs and self._coeffs._is_nonzero(self._const)

    def is_null(self):
        return not self._coeffs and self._coeffs._is_zero(self._const)
        
    def is_unique(self):
        return len(self._coeffs)==1
        
    def is_wellformed(self):
        assert is_num(self._const)
        return all( is_var(var) and is_num(coeff) for var,coeff in self._coeffs.items() )

    def _mul_term(self,term):
        assert is_num(term)
        val = term
        assert self.is_wellformed()
        for var in self._coeffs:
            self._coeffs[var] *= val;
        self._const *= val
        return self
        
    def _add_var_times_coeff(self,var,coeff):
        self._coeffs[var] += coeff
        return self

    def _add_term(self, term, coeff=1):
        assert self.is_wellformed()
        if is_num(term):
            self._const += term * coeff
        elif is_var(term):
            self._add_var_times_coeff(term,coeff)
        elif is_expr(term):
            for subterm,subcoeff in term._coeffs.items():
                self._add_term( subterm, subcoeff )
            self._const += term._const
        return self
        
    def evaluate(self, system = None):
        return self._const + sum( coeff * term.evaluate(system) for term,coeff in self._coeffs.items() )
        
    def is_undef(self, system = None):
        return not self.is_def(system)

    def is_def(self, system = None):
        return is_def( self.evaluate(system) )
        
    def _format_frac(self, frac, var_name = None):
        num_str = self._format_num(frac.numerator, var_name)
        den_str = "" if frac.denominator==1 else "/" + str(frac.denominator)
        return num_str + den_str
        
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
    def __init__( self, lhs, mod = None, _init_zero_expr=None ):
        if _init_zero_expr is None:
            assert not is_equ(lhs)
            self._mod = mod
            self._zero_expr = Expr(lhs,mod=mod).normalised(mod)
        else:
            self._mod = mod
            self._zero_expr = _init_zero_expr
            self._zero_expr._mod = mod
        
    def __bool__(self):
        # For constraints applied to the global default system eg. "a[:]=2", can be used directly eg. "a==2" is True
        # For constraints applied to a specific system eg. "sys.constrain(a*2==2)", checks for tautology, eg. "a==a" is True
        # To compare actual values, use sys.evaluate(a==1).
        if self.is_tautology():
            return True
        else:
            # For backwards compatibility return True if evaluates to true, else false if Undefined or False
            # In fact, we should stop using Equs for this.
            # Would like to return _Undefined(), but Python doesn't support it
            return self.evaluate()
            # return False
            
    def reduce_by_equ_for_var(self,equ,var):
        assert 1 == equ.coefficient(var), str.join(' ',("Expected 1 as coeff of ",repr(var),"in",repr(equ)))
        return (self - self.coefficient(var) * equ).set_coeff(var,0)
    
    def set_coeff(self,var,coeff):
        self._zero_expr.set_coeff(var,coeff)
        return self
    
    @staticmethod
    def _z(a,b):
        assert a==b # Solver should work combining equ with different mods, but not confirmed
        return a

    def __add__ (self, other): assert is_equ(other); return EquZero(self._zero_expr+other._zero_expr, mod=self._z(self._mod,other._mod))
    def __sub__ (self, other): assert is_equ(other); return EquZero(self._zero_expr-other._zero_expr, mod=self._z(self._mod,other._mod))
    def __mul__ (self, other): assert is_equ(other); return EquZero(self._zero_expr*other, mod=self._mod)
    def __rmul__(self, other): assert is_num(other); return EquZero(self._zero_expr*other, mod=self._mod)
    def __truediv__ (self, other): assert is_num(other); return EquZero( self._zero_expr*self._inverse(other), mod=self._mod)
    def __div__ (self, other): return self.__truediv__(other)
    def __or__(self,other): return self.evaluate() | other
    def __ror__(self,other): return other | self.evaluate()
    def __and__(self,other): return self.evaluate() & evaluate(other)
    def __rand__(self,other): return evaluate(other) & self.evaluate()
    
    def __eq__(self,other):
        # Test for equivalance between equations,
        # ie. (a==2) == (a==2) regardless of which systems a is defined in but (a==2) != (-a==-2)
        # Used list.remove(equ) and in [equ1, equ2] == [equ1, equ2]
        return is_equ(other) and self._mod==other._mod and (self._zero_expr-other._zero_expr).is_null()
    
    def _inverse(self, val):
        return self._zero_expr._inverse(val,mod=self._mod)
    
    def normalised_for(self,n_var):
        return EquZero(None,mod=self._mod,_init_zero_expr=self._zero_expr.normalised_for(n_var))
    
    def mod(self,n):
        assert self._mod is None
        return EquZero(self._zero_expr.mod(n), mod=n)
    
    def is_tautology(self):
        return self._zero_expr.is_null()
    
    def is_contradiction(self):
        return self._zero_expr.is_nonnull()
    
    def solve_for_var(self, var, undef=None):
        coeff = self._zero_expr.coefficient(var)
        #soln = self._zero_expr.minus_excluding(var) * self._inverse(coeff)
        soln = Expr(coeff*var-self._zero_expr,mod=self._mod) * self._inverse(coeff)
        if self._zero_expr.is_unique():
            return soln.normalised(self._mod).evaluate()
        else:
            return undef
        
    def evaluate(self, system = None):
        # Will return True, False, or undefined
        val = self._zero_expr.evaluate(system)
        return (val) if is_undef(val) else (val==0)
        
    def is_def(self, system = None):
        return is_def( self.evaluate(system) )

    def copy(self):
        return EquZero(self._zero_expr.copy(), mod=self._mod)
    
    def coefficient(self,variable):
        return self._zero_expr.coefficient(variable)
    
    def variables(self):
        return self._zero_expr.variables()
        
    def rhs_constant(self):
        return -self._zero_expr.const()
        
    def __repr__(self):
        return "{ 0 = " + repr(self._zero_expr) + (" mod" + str(self._mod) if self._mod is not None else "") + " }"

def Equ(lhs,rhs):
    return EquZero(lhs-rhs)

class System(Canonical):
    def __init__(self, *constraints):
        super(System, self).__init__( constraints, undef = _Undefined() )
        self._orig_constraints = list(constraints)
        
    def try_constrain(self,equ):
        return if_raises(Contradiction, self.constrain, equ)
    
    def constrain(self,*args, **kwargs):
        mod = kwargs.get('mod',None)
        for equ in args:
            assert is_equ(equ)
            self.add_constraint(equ.mod(mod))
            self._orig_constraints.append(equ.mod(mod))
    
    def evaluate(self,evaluand):
        if is_var(evaluand):
            return self.var_value( evaluand )
        elif is_bool(evaluand) or is_undef(evaluand) or is_num(evaluand):
            return evaluand
        elif is_expr(evaluand) or is_equ(evaluand):
            return evaluand.evaluate(self)
        else:
            assert 0

def undefined():
    # Note: _Undefined used internally, but we return None or 'undefined' so caller can do "if aa == 'undefined'"
    return 'undefined'
    # return None
        
class _Undefined:
    def __eq__  (self,other): return other==undefined() # Not equal to self
    def __bool__(self):       return False
    def __add__ (self,other): return self
    def __radd__(self,other): return self
    def __sub__ (self,other): return self
    def __rsub__(self,other): return self
    def __mul__ (self,other): return 0 if other==0 else self
    def __rmul__(self,other): return 0 if other==0 else self
    def __repr__(self): return "_Undefined"
    def __str__(self): return str(undefined())
    def __or__  (self, other): return True if other else self
    def __ror__ (self, other): return True if other else self
    def __and__ (self, other): return False if evaluate(other)==False else _Undefined()
    def __rand__(self, other): return False if evaluate(other)==False else _Undefined()

_default_sys = System()
_solve_debug_print = ignore # Used for debugging

default_vars = Varset() # For convenience, one we can import, even though we can define variables in other ways

def default_sys(): return _default_sys

# Only use these outside the module, inside use _default_sys.blah() or default_sys().blah() directly

def constrain(*args, **kwargs): return default_sys().constrain( *args, **kwargs )
def evaluate(e):                return default_sys().evaluate( e )
def internals():                return default_sys().variables()
def solved():                   return default_sys().solved()
def constraints():              return default_sys().constraints()

def reset_internals():
    # Used for testing systemwide constraints multiple times
    global _default_sys
    global _solve_debug_print
    _default_sys = System()
    Var._next_var_idx = 0
    _solve_debug_print = ignore
    