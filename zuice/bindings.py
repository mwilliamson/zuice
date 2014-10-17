class Bindings(object):
    def __init__(self):
        self._bindings = {}
    
    def bind(self, key, provider=None):
        if key in self:
            raise AlreadyBoundException("Cannot rebind key: %s" % key)
            
        if provider is None:
            return Binder(key, self)
        else:
            self._force_bind(key, provider)
    
    def _force_bind(self, key, provider):
        self._bindings[key] = provider
    
    def copy(self):
        copy = Bindings()
        copy._bindings = self._bindings.copy()
        return copy
    
    def update(self, bindings):
        for key in bindings._bindings:
            if key in self._bindings:
                raise AlreadyBoundException("Key already bound: %s" % key)
        self._bindings.update(bindings._bindings)
    
    def __contains__(self, key):
        return key in self._bindings
        
    def __getitem__(self, key):
        return self._bindings[key]
    
    def get(self, key):
        return self._bindings.get(key, lambda injector: injector._get_from_type(key))

class Binder(object):
    def __init__(self, key, bindings):
        self._key = key
        self._bindings = bindings
    
    def to_instance(self, instance):
        return self.to_provider(lambda injector: instance)
    
    def to_key(self, key):
        if key is self._key:
            raise TypeError("Cannot bind a key to itself")
        return self.to_provider(lambda injector: injector.get(key))
    
    def to_type(self, key):
        return self.to_key(key)
    
    def to_provider(self, provider):
        self._bindings.bind(self._key, provider)
        return self
    
    def singleton(self):
        current_provider = self._bindings.get(self._key)
        self._bindings._force_bind(self._key, SingletonProvider(current_provider))
        return self


class SingletonProvider(object):
    def __init__(self, provider):
        self._instantiated = False
        self._provider = provider
    
    def __call__(self, injector):
        if self._instantiated:
            return self._value
        else:
            self._value = self._provider(injector)
            self._instantiated = True
            return self._value


class AlreadyBoundException(Exception):
    pass
