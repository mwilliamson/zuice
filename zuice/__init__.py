import zuice.inspect

class Injector(object):
    def __init__(self, bindings):
        self._bindings = bindings.copy()
        self._bindings.bind('injector').to_instance(self)
        self._bindings.bind(Injector).to_instance(self)
    
    def get(self, key):
        if isinstance(key, basestring):
            return self.get_from_name(key)
        if isinstance(key, type):
            return self.get_from_type(key)
        raise NoSuchBindingException(key)
    
    def get_from_type(self, type_to_get):
        if not isinstance(type_to_get, type):
            raise TypeError(str(type_to_get) + " is not a type")
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
            zuice_constructor = method.zuice
        else:
            zuice_constructor = _ZuiceConstructorByName(method, zuice.inspect.get_args_spec)
        return self._inject(method, zuice_constructor)
        try:
            return method()
        except TypeError:
            raise NoSuchBindingException(method)
    
    def _get_from_bindings(self, key):
        if key not in self._bindings:
            raise NoSuchBindingException(key)
        return self.call(self._bindings[key])
        
    def _inject(self, to_call, argument_builder):
        args = argument_builder.build_args(self)
        return to_call(*args.args, **args.kwargs)

class NoSuchBindingException(Exception):
    def __init__(self, key):
        self.key = key
        
    def __str__(self):
        return str(self.key)

class _Arguments(object):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

class _ZuiceConstructorByName(object):
    def __init__(self, method, argument_inspector):
        self._method = method
        self._argument_inspector = argument_inspector
    
    def build_args(self, injector):
        args_spec = self._argument_inspector(self._method)
        def build_arg(arg):
            if arg.name in injector._bindings:
                return injector.get_from_name(arg.name)
            if arg.has_default:
                return arg.default
            raise NoSuchBindingException(arg.name)
        return _Arguments(map(build_arg, args_spec), {})
        
def inject_by_name(constructor):
    constructor.zuice = _ZuiceConstructorByName(constructor, zuice.inspect.get_args_spec)
    return constructor

class _ZuiceConstructorByNamedKey(object):
    def __init__(self, method, keys, named_keys):
        self._method = method
        self._keys = keys
        self._named_keys = named_keys
        
    def build_args(self, injector):
        args_spec = zuice.inspect.get_args_spec(self._method)
        arg_names = [arg.name for arg in args_spec]
        
        keys = self._named_keys.copy()
        for index in range(0, len(self._keys)):
            keys[arg_names[index]] = self._keys[index]
        
        def build_arg(arg):
            if arg.name in keys:
                return injector.get(keys[arg.name])
            try:
                return injector.get(arg.name)
            except NoSuchBindingException:
                if arg.has_default:
                    return arg.default
                raise NoSuchBindingException(arg.name)
        args = map(build_arg, args_spec)
        
        kwargs = {}
        for key in self._named_keys:
            if key not in arg_names:
                kwargs[key] = injector.get(self._named_keys[key])
            
        return _Arguments(args, kwargs)

def inject_with(*keys, **named_keys):
    def a(constructor):
        zuice_constructor = _ZuiceConstructorByNamedKey(constructor, keys, named_keys)
        constructor.zuice = zuice_constructor
        return constructor
    return a
