class Bindings(object):
    def __init__(self):
        self._bindings = {}
    
    def bind(self, key):
        if key in self:
            raise AlreadyBoundException("Cannot rebind key: %s" % key)
        return Binder(key, self._bindings)
    
    def copy(self):
        copy = Bindings()
        copy._bindings = self._bindings.copy()
        return copy
    
    def update(self, bindings):
        self._bindings.update(bindings._bindings)
    
    def __contains__(self, key):
        return key in self._bindings
        
    def __getitem__(self, key):
        return self._bindings[key]

class Binder(object):
    def __init__(self, key, bindings):
        self._bound = False
        self._key = key
        self._bindings = bindings
    
    def to_instance(self, instance):
        self.to_provider(lambda: instance)
    
    def to_key(self, key):
        if key is self._key:
            raise TypeError("Cannot bind a key to itself")
        self.to_provider(lambda injector: injector.get(key))
    
    def to_type(self, key):
        return self.to_key(key)
    
    def to_provider(self, provider):
        if self._bound:
            raise AlreadyBoundException()
        self._bound = True
        self._bindings[self._key] = provider

class AlreadyBoundException(Exception):
    pass
