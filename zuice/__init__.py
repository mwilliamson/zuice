import zuice.inspect

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
            raise TypeError, str(type_to_get) + " is not a type"
        if type_to_get in self.bindings:
            return self._get_from_bindings(type_to_get)
        if hasattr(type_to_get.__init__, 'zuice'):
            return self._inject(type_to_get)
        try:
            return type_to_get()
        except TypeError:
            raise NoSuchBindingException(type_to_get)
        
    def get_from_name(self, name):
        if not isinstance(name, basestring):
            raise TypeError
        return self._get_from_bindings(name)
    
    def call(self, method):
        if hasattr(method, 'zuice'):
            args = method.zuice.build_args(self)
            return method(*args)
        try:
            return method()
        except TypeError:
            raise NoSuchBindingException(method)
    
    def _get_from_bindings(self, key):
        if key not in self.bindings:
            raise NoSuchBindingException(key)
        return self.bindings[key](self)
        
    def _inject(self, type):
        args = type.__init__.zuice.build_args(self)
        return type(*args)

class NoSuchBindingException(Exception):
    def __init__(self, key):
        self.key = key
        
    def __str__(self):
        return str(self.key)

class _ZuiceConstructorByName(object):
    def __init__(self, method):
        self._method = method
    
    def build_args(self, injector):
        args_spec = zuice.inspect.get_method_args_spec(self._method)
        def build_arg(arg):
            if arg.name in injector.bindings:
                return injector.get_from_name(arg.name)
            if arg.has_default:
                return arg.default
            raise NoSuchBindingException(arg.name)
        return map(build_arg, args_spec)
        
def inject_by_name(constructor):
    constructor.zuice = _ZuiceConstructorByName(constructor)
    return constructor

class _ZuiceConstructorByKey(object):
    def __init__(self, types):
        self.types = types
    
    def build_args(self, injector):
        return map(lambda type: injector.get(type), self.types)

def inject_with(*keys):
    def a(constructor):
        zuice_constructor = _ZuiceConstructorByKey(keys)
        constructor.zuice = zuice_constructor
        return constructor
    return a
