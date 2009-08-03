class Bindings(object):
    def __init__(self):
        self._bindings = {}
    
    def bind(self, key):
        if isinstance(key, basestring):
            return self.bind_name(key)
        if isinstance(key, type):
            return self.bind_type(key)
        raise InvalidBindingException
    
    def bind_type(self, type_to_bind):
        return self._type_safe_bind(type, type_to_bind)
    
    def bind_name(self, name):
        return self._type_safe_bind(basestring, name)
    
    def _type_safe_bind(self, type, key):
        if not isinstance(key, type):
            raise InvalidBindingException()
        return Binder(key, self._bindings)
    
    def copy(self):
        copy = Bindings()
        copy._bindings = self._bindings.copy()
        return copy
        
    def __contains__(self, key):
        return key in self._bindings
        
    def __getitem__(self, key):
        return self._bindings[key]

class InvalidBindingException(Exception):
    pass

class Binder(object):
    def __init__(self, key, bindings):
        self._bound = False
        self._key = key
        self._bindings = bindings
    
    def to_instance(self, instance):
        self.to_provider(lambda injector: instance)
        
    def to_type(self, type_to_get):
        if type_to_get is self._key:
            raise TypeError, "Cannot bind a type to itself"
        if not isinstance(type_to_get, type):
            raise TypeError, "to_type can only bind to types"
        self.to_provider(lambda injector: injector.get_from_type(type_to_get))
    
    def to_name(self, name):
        if name == self._key:
            raise TypeError, "Cannot bind a name to itself"
        if not isinstance(name, basestring):
            raise TypeError, "to_name can only bind to strings"
        self.to_provider(lambda injector: injector.get_from_name(name))
        
    
    def to_provider(self, provider):
        if self._bound:
            raise AlreadyBoundException()
        self._bound = True
        self._bindings[self._key] = provider

class AlreadyBoundException(Exception):
    pass
