:mod:`zuice`
============

.. module:: zuice

.. class:: Injector

    .. method:: __init__(bindings)
    
        Create an injector with the given bindings, which is assumed to be of
        type :class:`~zuice.bindings.Bindings`
    
    .. method:: get(key)
    
        If key is a :class:`type`, this is the same as calling ``get_from_type(key)``.
        If key is a :class:`basestring`, this is the same as calling ``get_from_name(key)``.
        Otherwise, :class:`~zuice.NoSuchBindingException` is raised.
    
    .. method:: get_from_type(key)
    
        If key has been bound, then use the appropriate binding.
        
        Otherwise, if an injection decorator has been applied to
        ``key.__init__``, attempt to construct the passed type by injecting
        its arguments.
        
        Finally, attempt to call the constructor with no arguments. If this
        fails, :class:`~zuice.NoSuchBindingException` is raised.
    
    .. method:: get_from_name(key)
    
        If key has been bound, then use the appropriate binding.
        Otherwise, :class:`~zuice.NoSuchBindingException` is raised.
    
    .. method:: call(function)
    
        Try to call function by injecting its arguments. If no injection decorator
        has been applied to the function, attempt to inject the arguments by name.
        Otherwise, inject its arguments in the manner specified by the decorator.

.. function:: inject_by_name()

    Indicates that a function or method should be injected by name. For instance::
    
        class Apple(object):
            @inject_by_name
            def __init__(self, foo, bar):
                pass
                
        apple = injector.get(Apple)
        
    is roughly equivalent to::
    
        class Apple(object):
            def __init__(self, foo, bar):
                pass
        
        apple = Apple(injector.get("foo"), injector.get("bar"))
        
    If a binding for a given name cannot be found, but a default value is specified,
    that default value is used.

.. function:: inject_with(*keys, **named_keys)

    Indicates that a function or method should be injected using the keys
    specified, with the nth key matching up with the nth argument. For instance::
    
        class Apple(object):
            @inject_with(Foo, "default_bar")
            def __init__(self, foo, bar):
                pass
                
        apple = injector.get(Apple)
        
    is roughly equivalent to::
    
        class Apple(object):
            def __init__(self, foo, bar):
                pass
                
        apple = Apple(injector.get(Foo), injector.get("default_bar"))
        
    If there are fewer keys specified than arguments, the remaining arguments
    use their default values, if they have any -- otherwise, the injection fails.
    
    If instead :func:`inject_with` is called with keyword arguments only, each key
    is matched up to the name of the argument accordingly. For instance::
    
        class Apple(object):
            @inject_with(baz="default_baz", foo=Foo)
            def __init__(self, foo, bar="bar", baz="baz"):
                pass
                
        apple = injector.get(Apple)
        
    is roughly equivalent to::
    
        class Apple(object):
            def __init__(self, foo, bar="bar", baz="baz"):
                pass
                
        apple = Apple(foo=injector.get(Foo), baz=injector.get("default_baz"))
        
    The behaviour of this decorator when called with both non-keyword and keyword
    arguments is undefined.
    
    
