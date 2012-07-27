

class Wire:
    # TODO: Array of settors if multiple nodes set value to same number?
    
    def __init__(self):
        self._settor = None
        self._value = None
        self._neighbours = []
        
    def set(self, settor, value):
        if settor != self._settor :
            self._value = value
            self._settor = settor
            self.notify_all_but(self._settor, _value)
        elif self._settor :
            assert self._value == value
            
    def notify_all_but(self, but, value):
        for node in self._neighbours:
            if node != but: node.notify(value);
    
    def attach(self, *nodes):
        self.neighbours.extend(nodes)
        
    def revoke(self, node):
        if self._value and self._settor == node:
            self._value = self._settor = None
            self.notify_all_but(node, None)
            
    def val(self, querent):
        return self._value if querent is not self._settor else None
    

class Node:
    def __init__(self, wires):
        self._wires = wires
        for wire in wires:
            wire.attach(self)
        
    def notify(self):
        self.func(wires)
        
    
        
        