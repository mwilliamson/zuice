import zuice.inspect

class Injector(object):
    def __init__(self, bindings):
        self._bindings = bindings.copy()
    
    def get(self, key):
        if isinstance(key, basestring):
            return self.get_from_name(key)
        if isinstance(key, type):
            return self.get_from_type(key)
        raise NoSuchBindingException(key)
    
    def get_from_type(self, type_to_get):
        if not isinstance(type_to_get, type):
            raise TypeError, str(type_to_get) + " is not a type"
        if type_to_get in self._bindings:
            return self._get_from_bindings(type_to_get)
        if hasattr(type_to_get.__init__, 'zuice'):
            return self._inject(type_to_get, type_to_get.__init__.zuice)
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
            return self._inject(method, method.zuice)
        try:
            return method()
        except TypeError:
            raise NoSuchBindingException(method)
    
    def _get_from_bindings(self, key):
        if key not in self._bindings:
            raise NoSuchBindingException(key)
        return self._bindings[key](self)
        
    def _inject(self, to_call, argument_builder):
        args = argument_builder.build_args(self)
        return to_call(*args)

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
            if arg.name in injector._bindings:
                return injector.get_from_name(arg.name)
            if arg.has_default:
                return arg.default
            raise NoSuchBindingException(arg.name)
        return map(build_arg, args_spec)
        
def inject_by_name(constructor):
    constructor.zuice = _ZuiceConstructorByName(constructor)
    return constructor

class _ZuiceConstructorByKey(object):
    def __init__(self, keys):
        self._keys = keys
    
    def build_args(self, injector):
        return map(lambda key: injector.get(key), self._keys)

class _ZuiceConstructorByNamedKey(object):
    def __init__(self, method, keys):
        self._method = method
        self._keys = keys
        
    def build_args(self, injector):
        args_spec = zuice.inspect.get_method_args_spec(self._method)
        def build_arg(arg):
            if arg.name in self._keys:
                return injector.get(self._keys[arg.name])
            try:
                return injector.get(arg.name)
            except NoSuchBindingException:
                if arg.has_default:
                    return arg.default
                raise NoSuchBindingException(arg.name)
        return map(build_arg, args_spec)

def inject_with(*keys, **named_keys):
    def a(constructor):
        if len(named_keys) > 0:
            zuice_constructor = _ZuiceConstructorByNamedKey(constructor, named_keys)
        else:
            zuice_constructor = _ZuiceConstructorByKey(keys)
        constructor.zuice = zuice_constructor
        return constructor
    return a
