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
        new = self._construct(type_to_get)
        self._inject_members(new)
        return new
        
    def get_from_name(self, name):
        if not isinstance(name, basestring):
            raise TypeError
        return self._get_from_bindings(name)
    
    def call(self, method):
        if hasattr(method, 'zuice'):
            zuice_constructor = method.zuice
        else:
            zuice_constructor = _ZuiceConstructorByNamedKey(method, [], {})
        return self._inject(method, zuice_constructor)
    
    def _get_from_bindings(self, key):
        if key not in self._bindings:
            raise NoSuchBindingException(key)
        return self.call(self._bindings[key])
        
    def _inject(self, to_call, argument_builder):
        args = argument_builder.build_args(self)
        return to_call(*args.args, **args.kwargs)
    
    def _construct(self, type_to_construct):
        if hasattr(type_to_construct.__init__, 'zuice'):
            return self._inject(type_to_construct, type_to_construct.__init__.zuice)
        try:
            return type_to_construct()
        except TypeError:
            raise NoSuchBindingException(type_to_construct)
    
    def _inject_members(self, new):
        clazz = type(new)
        for key in clazz.__dict__:
            attr = getattr(clazz, key)
            if isinstance(attr, InjectedMember):
                setattr(new, key, attr.inject(self))


class NoSuchBindingException(Exception):
    def __init__(self, key):
        self.key = key
        
    def __str__(self):
        return str(self.key)

class _Arguments(object):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs
        
def inject_by_name(constructor):
    return inject_with()(constructor)

class _ZuiceConstructorByNamedKey(object):
    def __init__(self, method, keys, named_keys):
        self._named_keys = named_keys
        self._args_spec = zuice.inspect.get_args_spec(method)
        self._arg_names = [arg.name for arg in self._args_spec]
        
        self._keys = named_keys.copy()
        for index in range(0, len(keys)):
            arg_name = self._arg_names[index]
            if arg_name in named_keys:
                raise TypeError("The argument " + arg_name + " is overspecified")
            self._keys[arg_name] = keys[index]
        
    def build_args(self, injector):
        def build_arg(arg):
            if arg.name in self._keys:
                return injector.get(self._keys[arg.name])
            if arg.name in injector._bindings:
                return injector.get(arg.name)
            if arg.has_default:
                return arg.default
            raise NoSuchBindingException(arg.name)
        args = map(build_arg, self._args_spec)
        
        kwargs = {}
        for key in self._named_keys:
            if key not in self._arg_names:
                kwargs[key] = injector.get(self._named_keys[key])
            
        return _Arguments(args, kwargs)

def inject_with(*keys, **named_keys):
    def a(constructor):
        zuice_constructor = _ZuiceConstructorByNamedKey(constructor, keys, named_keys)
        constructor.zuice = zuice_constructor
        return constructor
    return a

class ZuiceConstructorForMembers(object):
    def __init__(self, members):
        self._members = members
    
    def build_args(self, injector):
        kwargs = {}
        
        for key in self._members:
            kwargs[key] = injector.get(self._members[key])
        
        return _Arguments([], kwargs)

def inject_members(**members):
    def create_constructor(constructor):
        def assign_members(self, *args, **kwargs):
            for member in members:
                if member not in kwargs:
                    raise TypeError("Missing keyword argument: %s" % member)
                setattr(self, member, kwargs.pop(member))
            constructor(self, *args, **kwargs)
        
        assign_members.zuice = ZuiceConstructorForMembers(members)
        return assign_members
        
    return create_constructor

class InjectedMember(object):
    def __init__(self, key):
        self._key = key
        
    def inject(self, injector):
        return injector.get(self._key)

def inject(key):
    return InjectedMember(key)

class Injectable(object):
    pass
