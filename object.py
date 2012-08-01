# Pylogram libraries
from expressions import constrain, Contradiction, Var, Expr, is_expr, is_var, is_num
from helpers import *

def is_obj(obj):
    return isinstance(obj,Obj)

def set_name(obj,name,overwrite=False):
    if is_var(obj) or is_obj(obj):
        if overwrite or obj.is_anon():
            obj.set_name(name)
    elif is_expr(obj) or is_num(obj):
        return
    else:
        assert 0
        
    
class Obj:
    def _require_init(self):
        if '_vars' not in self.__dict__:
            self.__dict__['_vars'] = {}
            self._name=""

    def __setattr__(self,attr,val):
        self._require_init()
        if attr in self._vars:
            if is_obj(self._vars[attr]):
                self._vars[attr].constrain_equal( val )
            else:
                Expr(self._vars[attr]).constrain_equal( val )
        elif attr[0]=="_":
            self.__dict__[attr] = val
        else:
            self.make_var(attr,val)

    default_arg = DefaultArg()
    def make_var(self,attr, val = default_arg):
        self._vars[attr] = val if val is not self.default_arg else Var(prefer=float)
        name = (self._name+ "."*bool(self._name))+attr
        set_name(self._vars[attr],name,overwrite=False)
        return self._vars[attr]
            
    def __getattr__(self,attr):
        self._require_init()
        if attr in self._vars:
            return self._vars[attr]
        else:
            return self.make_var(attr)
        
    def set_name(self,new_name):
        self._name = new_name
        for subname, subobj in self._vars.items():
            set_name(subobj,new_name+"."+subname)
            
    def is_anon(self):
        return not self._name
    
    def __eq__(self,other):
        return is_obj(other) and self._vars.keys() == other._vars.keys() and undef_eq(self._vars.values(),other._vars.values())

    def constrain_equal(self,other):
        assert is_obj(other)
        assert self._vars.keys() == other._vars.keys()
        for a,b in zip(self._vars.values(),other._vars.values()):
            if is_obj(a):
                a.constrain_equal(b)
            else:
                Expr(a).constrain_equal(b)

    def __setitem__(self, emptyslice, rhs):
        # Support "a [:]= b" syntax
        assert emptyslice == slice(None, None, None)
        self.constrain_equal(rhs)
    
    def reduce_subobj(self, subobj, subfunc, arg):
        # TODO: Use try/except.
        if is_obj(subobj):
            return getattr(subobj,subfunc)(arg)
        else:
            # TODO: For undef and similar make this function into an "all"
            # Literals, Vars and anything else won't be drawn on screen
            return arg
    
    def reduce_subobjs(self, subfunc, arg):
        assert type(self) != type(Obj()) # Should be derived class, not Obj itself, else will recurse
        for subobj in self._vars.values():
            arg = self.reduce_subobj( subobj, subfunc, arg )
        return arg

class InitorArray(Obj):
    def __init__(self,Type,*args_of_args, name=""):
        self._arr = [ Type(*args) for args in args_of_args ]
        self.N = len(self._arr)
        self.set_name(name)
        self.first = self._arr[0]
        self.last = self._arr[-1]
        
    def set_name(self,name):
        for idx in range(self.N): set_name(self._arr[idx],name+"["+str(idx)+"]")

    def __setitem__(self,idx,val):
        if idx==slice(None, None, None):
            super().__setitem__(idx,val)
        else:
            assert 0 <= idx <= self.N
            self._arr[idx].constrain_equal(val)
        
    def __getitem__(self,idx):
        return self._arr[idx]
        
    def adj_objs(self, n=2):
        return ( self._arr[i:i+n] for i in range(self.N+1-n) )

    def __iter__(self):
        return iter(self._arr)
        
    def __repr__(self):
        return repr(self._arr)
        
    def __eq__(self,other):
        return undef_eq( self, other )

    def reduce_subobjs(self, subfunc, arg):
        # assert type(self) == type(Array()) 
        for subobj in self._arr:
            arg = self.reduce_subobj(  subobj, subfunc, arg )
        return super().reduce_subobjs(subfunc, arg)

    # TODO: Enable sim_draw() and draw() only if enabled for subobjs
    def sim_draw(self, str=""):
        return self.reduce_subobjs('sim_draw', str)
        
    def draw(self, canvas):
        return self.reduce_subobjs('draw',canvas)
        
        
class Array(InitorArray):
    def __init__(self,N,Type,name=""):
        # TODO: Do we want to support non-var use, eg. arr1 = Array(N); arr1.first = 1; arr1.each = arr1.prev*2
        super().__init__(Type, *(() for _ in range(N)), name=name )
