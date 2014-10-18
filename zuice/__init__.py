import itertools

import zuice.reflect
from .bindings import Bindings

__all__ = ['Bindings', 'Injector', 'Base', 'dependency']

class Injector(object):
    def __init__(self, bindings, _parent_injector=None):
        self._bindings = bindings.copy()
        self._parent_injector = _parent_injector
        self._singletons = {}
    
    def get(self, key, instances=None):
        if instances:
            injector = self._extend_with_instances(instances)
            return injector.get(key)
        else:
            return self._get_by_key(key)
    
    def _extend_with_instances(self, instances):
        bindings = Bindings()
        for key in instances:
            bindings.bind(key).to_instance(instances[key])
        return self._extend_with_bindings(bindings)
        
    def _extend_with_bindings(self, bindings):
        return Injector(bindings, self)
    
    def _get_by_key(self, key):
        if key == Injector:
            return self
        
        elif key in self._bindings:
            return self._get_from_binding(self._bindings[key])
            
        elif isinstance(key, type):
            return self._get_from_type(key)
        
        elif self._parent_injector is not None:
            return self._parent_injector.get(key)
        
        else:
            raise NoSuchBindingException(key)
    
    def _get_from_binding(self, binding):
        if binding.is_singleton:
            if binding not in self._singletons:
                self._singletons[binding] = binding.provider(self)
            
            return self._singletons[binding]
        else:
            return binding.provider(self)
        
    
    def _get_from_type(self, type_to_get):
        if hasattr(type_to_get.__init__, '_zuice'):
            return type_to_get(___injector=self)
        
        elif zuice.reflect.has_no_arg_constructor(type_to_get):
            return type_to_get()
        
        else:
            raise NoSuchBindingException(type_to_get)


class NoSuchBindingException(Exception):
    def __init__(self, key):
        self.key = key
        
    def __str__(self):
        return str(self.key)


_param_counter = itertools.count()


class _Parameter(object):
    pass


class _Dependency(_Parameter):
    def __init__(self, key):
        self._key = key
        self._ordering = next(_param_counter)
    
    def inject(self, injector):
        return injector.get(self._key)


def dependency(key):
    return _Dependency(key)


class _Key(object):
    def __init__(self, name):
        self._name = name
    
    def __repr__(self):
        return "Key({0})".format(repr(self._name))
    

def key(name):
    return _Key(name)


class Base(object):
    def __init__(self, *args, **kwargs):
        attrs = []
        for key in dir(type(self)):
            attr = getattr(self, key)
            if isinstance(attr, _Parameter):
                attrs.append((key, attr))
            
        if '___injector' in kwargs:
            injector = kwargs.pop('___injector')
            for key, attr in attrs:
                setattr(self, key, attr.inject(injector))
        else:
            if len(args) > len(attrs):
                raise TypeError(
                    "__init__ takes exactly %s arguments (%s given)" %
                        (len(attrs) + 1, len(args) + 1)
                )
            attrs.sort(key=lambda item: item[1]._ordering)
            for index, (key, attr) in enumerate(attrs):
                arg_name = _key_to_arg_name(key)
                
                if index < len(args):
                    if arg_name in kwargs:
                        raise TypeError("Got multiple values for keyword argument '%s'" % arg_name)
                    setattr(self, key, args[index])
                elif arg_name in kwargs:
                    setattr(self, key, kwargs.pop(arg_name))
                else:
                    raise _missing_keyword_argument_error(arg_name)
        
        _check_keyword_arguments_consumed(kwargs)
    
    __init__._zuice = True


def _key_to_arg_name(key):
    return key.lstrip("_")


def _missing_keyword_argument_error(key):
    return TypeError("Missing keyword argument: %s" % key)


def _unexpected_keyword_argument_error(key):
    raise TypeError("Unexpected keyword argument: " + key)


def _check_keyword_arguments_consumed(kwargs):
    if len(kwargs) > 0:
        raise _unexpected_keyword_argument_error(next(iter(kwargs.keys())))
    
