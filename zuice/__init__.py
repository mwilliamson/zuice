class Bindings(object):
    def __init__(self):
        self.bindings = {}
    
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
        return Binder(key, self.bindings)
    
    def copy(self):
        copy = Bindings()
        copy.bindings = self.bindings.copy()
        return copy
        
    def __contains__(self, key):
        return key in self.bindings

class InvalidBindingException(Exception):
    pass

class Binder(object):
    def __init__(self, key, bindings):
        self.bound = False
        self.key = key
        self.bindings = bindings
    
    def to_instance(self, instance):
        self.to_provider(lambda: instance)
    
    def to_provider(self, provider):
        if self.bound:
            raise AlreadyBoundException()
        self.bound = True
        self.bindings[self.key] = provider

class AlreadyBoundException(Exception):
    pass

class Injector(object):
    def __init__(self, bindings):
        self.bindings = bindings.copy()
    
    def get(self, key):
        if isinstance(key, basestring):
            return self.get_from_name(key)
        if isinstance(key, type):
            return self.get_from_type(key)
        raise NoSuchBindingException
    
    def get_from_type(self, type):
        return self._get_from_bindings(type)
        
    def get_from_name(self, name):
        return self._get_from_bindings(name)
        
    def _get_from_bindings(self, key):
        if key not in self.bindings:
            raise NoSuchBindingException()
        return self.bindings.bindings[key]()

class NoSuchBindingException(Exception):
    pass
