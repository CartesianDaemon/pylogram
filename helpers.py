# Standard modules
from numbers import Number
from collections import defaultdict

class Struct:
    pass
    
DefaultArg = Struct()
        
class nonzero_dict( defaultdict ): #TODO: Move int onto this line?
    def __init__(self):
        super(nonzero_dict,self)
        super(nonzero_dict,self).__init__(int)
        
    def keys(self):
        return { k for k,v in super(nonzero_dict,self).items() if v }

    def items(self):
        return { (k,v) for k,v in super(nonzero_dict,self).items() if v }
    
    def values(self):
        return { v for v in super(nonzero_dict,self).values() if v }
    
    def __len__(self):
        return count(self.keys())

    def __repr__(self):
        # TODO: delegate to super(super(self))
        return repr(dict(self))
        
    def __bool__(self):
        return bool(self.keys())

def first( it ):
    return next( iter(it) )
    
def count( it ):
    return len(tuple(it))