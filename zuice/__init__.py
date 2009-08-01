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
        self.to_provider(lambda injector: instance)
        
    def to_type(self, type_to_get):
        if type_to_get is self.key:
            raise TypeError, "Cannot bind a type to itself"
        if not isinstance(type_to_get, type):
            raise TypeError, "to_type can only bind to types"
        self.to_provider(lambda injector: injector.get_from_type(type_to_get))
    
    def to_name(self, name):
        if name == self.key:
            raise TypeError, "Cannot bind a name to itself"
        if not isinstance(name, basestring):
            raise TypeError, "to_name can only bind to strings"
        self.to_provider(lambda injector: injector.get_from_name(name))
        
    
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
        raise NoSuchBindingException(key)
    
    def get_from_type(self, type_to_get):
        if not isinstance(type_to_get, type):
            raise TypeError
        if hasattr(type_to_get.__init__, 'zuice'):
            return self._inject(type_to_get)
        return self._get_from_bindings(type_to_get)
        
    def get_from_name(self, name):
        if not isinstance(name, basestring):
            raise TypeError
        return self._get_from_bindings(name)
        
    def _get_from_bindings(self, key):
        if key not in self.bindings:
            raise NoSuchBindingException(key)
        return self.bindings[key](self)
        
    def _inject(self, type):
        args = type.__init__.zuice.build_args(type, self)
        return type(*args)

class NoSuchBindingException(Exception):
    def __init__(self, key):
        self.key = key
        
    def __str__(self):
        return str(self.key)

class ZuiceConstructorByName(object):
    def build_args(self, type, injector):
        arg_names = inspect.getargspec(type.__init__)[0]
        arg_names = arg_names[1:]
        return map(lambda arg_name: injector.get_from_name(arg_name), arg_names)
        
def inject_by_name(constructor):
    constructor.zuice = ZuiceConstructorByName()
    return constructor

class ZuiceConstructorByKey(object):
    def __init__(self, types):
        self.types = types
    
    def build_args(self, type, injector):
        return map(lambda type: injector.get(type), self.types)

def inject_by_type(*types):
    return inject_with(*types)

def inject_with(*keys):
    def a(constructor):
        zuice_constructor = ZuiceConstructorByKey(keys)
        constructor.zuice = zuice_constructor
        return constructor
    return a

class ZuiceConstructorNoArgs(object):
    def build_args(self, type, injector):
        return []

def inject(constructor):
    if len(inspect.getargspec(constructor)[0]) > 1:
        raise TypeError
    constructor.zuice = ZuiceConstructorNoArgs()
    return constructor
