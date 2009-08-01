import inspect

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
        if hasattr(type.__init__, 'zuice') and type.__init__.zuice.injectable:
            return self._inject(type)
        return self._get_from_bindings(type)
        
    def get_from_name(self, name):
        return self._get_from_bindings(name)
        
    def _get_from_bindings(self, key):
        if key not in self.bindings:
            raise NoSuchBindingException()
        return self.bindings[key]()
        
    def _inject(self, type):
        arg_names = inspect.getargspec(type.__init__)[0]
        arg_names = arg_names[1:]
        args = map(lambda arg_name: self.get_from_name(arg_name), arg_names)
        return type(*args)

class NoSuchBindingException(Exception):
    pass

def inject_by_name(constructor):
    class ZuiceConstructor(object):
        def __init__(self):
            self.injectable = True
            
    constructor.zuice = ZuiceConstructor()
    return constructor
