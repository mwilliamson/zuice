from sets import Set

import inspect
import itertools

import zuice.reflect
from zuice.util import factory

__all__ = ['Injector', 'inject_by_name', 'inject_with', 'inject_attrs',
           'Injectable', 'inject', "factory"]

class Injector(object):
    def __init__(self, bindings):
        self._bindings = bindings.copy()
        self._bindings.bind('injector').to_instance(self)
        self._bindings.bind(Injector).to_instance(self)
    
    def get(self, key):
        if key in self._bindings:
            return self.call(self._bindings[key])
            
        elif isinstance(key, type):
            return self._get_from_type(key)
        
        else:
            raise NoSuchBindingException(key)
    
    def _get_from_type(self, type_to_get):
        if hasattr(type_to_get.__init__, 'zuice'):
            return self._inject(type_to_get, type_to_get.__init__.zuice)
        if type_to_get.__init__ is object.__init__ or len(zuice.reflect.get_args_spec(type_to_get.__init__)) == 0:
            return type_to_get()
        raise NoSuchBindingException(type_to_get)
    
    def call(self, method):
        if hasattr(method, 'zuice'):
            zuice_constructor = method.zuice
        else:
            zuice_constructor = _ZuiceConstructorByNamedKey(method, [], {})
        return self._inject(method, zuice_constructor)
    
    def _inject(self, to_call, argument_builder):
        args, kwargs = argument_builder.build_args(self)
        return to_call(*args, **kwargs)
    
class NoSuchBindingException(Exception):
    def __init__(self, key):
        self.key = key
        
    def __str__(self):
        return str(self.key)

def inject_by_name(constructor):
    return inject_with()(constructor)

class _ZuiceConstructorByNamedKey(object):
    def __init__(self, method, keys, named_keys):
        self._named_keys = named_keys
        self._args_spec = zuice.reflect.get_args_spec(method)
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
            
        return args, kwargs

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
        
        for arg_name, key in self._members.iteritems():
            kwargs[arg_name] = injector.get(key)
        
        return [], kwargs

def inject_attrs(**members):
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

class Dependency(object):
    _counter = itertools.count()
    
    def __init__(self, key):
        self._key = key
        self._ordering = self._counter.next()
        
    def inject(self, injector):
        return injector.get(self._key)

def dependency(key):
    return Dependency(key)

class InjectableConstructor(object):
    def build_args(self, injector):
        return [], {"___injector": injector}

class Injectable(object):
    def __init__(self, *args, **kwargs):
        attrs = []
        for key in dir(type(self)):
            attr = getattr(self, key)
            if isinstance(attr, Dependency):
                attrs.append((key, attr))
            
        if '___injector' in kwargs:
            injector = kwargs.pop('___injector')
            for key, attr in attrs:
                setattr(self, key, attr.inject(injector))
        else:
            if len(args) > len(attrs):
                raise TypeError("%s requires %s injected member(s) (%s given)" % (type(self).__name__, len(attrs), len(args)))
            attrs.sort(key=lambda (key, attr): attr._ordering)
            for index, (key, attr) in enumerate(attrs):
                arg_name = key.lstrip("_");
                
                if index < len(args):
                    if arg_name in kwargs:
                        raise TypeError("Got multiple values for keyword argument '%s'" % arg_name)
                    setattr(self, key, args[index])
                elif arg_name in kwargs:
                    setattr(self, key, kwargs.pop(arg_name))
                else:
                    raise TypeError("Missing keyword argument: %s" % key)
        
        if len(kwargs) > 0:
            raise TypeError("Unexpected keyword argument: " + kwargs.items()[0][0])
    
    __init__.zuice = InjectableConstructor()
