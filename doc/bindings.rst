:mod:`zuice.bindings`
=====================

.. module:: zuice.bindings

.. class:: Bindings

    .. method:: bind(key)
    
        Create a :class:`Binder` for the given key. The key must either be an
        instance of :class:`type` or :class:`basestring`; otherwise, a 
        :class:`TypeError` is raised.
    
    .. method:: bind_type(type_to_bind)
    
        Create a :class:`Binder` for the given type. The key must be an
        instance of :class:`type`; otherwise, a :class:`TypeError` is raised.
    
    .. method:: bind_name(name)
    
        Create a :class:`Binder` for the given name. The key must be an
        instance of :class:`basestring`; otherwise, a :class:`TypeError` is raised.
    
    .. method:: copy()
    
        Create a copy of this :class:`Bindings` instance. Any further modifications
        to this instance will not modify the copy, and vice versa.
    
    .. method:: __contains__(key)
    
        Return :keyword:`True` if the key has been bound; :keyword:`False` otherwise.
    
    .. method:: __getitem__(key)
    
        If the key has been bound, return the provider for that key. Otherwise,
        raise :class:`KeyError`.

.. class:: Binder

    Each :class:`Binder` is created with a key. When using Zuice, you will rarely
    need to assign a :class:`Binder` to a variable. For instance, instead of::
    
        binder = bindings.bind("spam")
        binder.to_type(Spam)
        
    simply write::
    
        bindings.bind("spam").to_type(Spam)
        
    .. method:: to_provider(provider)
    
        The most powerful of all methods on :class:`Binder`, all other methods simply
        delegate to this one by creating various providers. A provider is a function
        that returns an instance for the key.
        
        For instance, let's say whenever we attempt to inject the name ``uuid_generator``,
        we want to return ``uuid.uuid4``. We could write this as::
        
            bindings.bind('uuid_generator').to_provider(lambda: uuid.uuid4)
            
        In this case, there is a convenience method, :func:`to_instance`, that
        has the same effect.
        
        Any arguments the provider has will be injected. Unless an injection
        decorator is used, the arguments will be injected by name.
        
        For instance, let's say we have a web application in which the
        request of an object is already bound to the name ``'request'``. However,
        in many cases, the only data we actually want from the request are
        the POST parameters. Therefore, we might decide to bind the name
        ``post_parameters`` like so (assuming the POST parameters are accessible
        by the attribute `post_parameters`)::
        
            bindings.bind('post_parameters').to_provider(lambda request: request.post_parameters)
            
        In Django, this is written as::
        
            def _request_to_post_parameters(request):
                if request.method == "POST":
                    return request.POST
                return None
        
            bindings.bind("post_parameters").to_provider(_request_to_post_parameters)

        Note that the parameters are :const:`None` if the request was not made
        by POST.

    .. method:: to_instance(instance)
    
        Bind the key to a specific instance. Whenever the injector attempts to
        get an instance associated with the key, this same instance will always
        be returned. Equivalent to calling ``to_provider(lambda: instance)``.
    
    .. method:: to_type(type_to_bind_to)
    
        Bind the key to a type. Whenever the injector attempts to get an instance
        associated with the key, it will attempt to inject the given type.
        Equivalent to calling ``to_provider(lambda injector: injector.get(type))``,
        except that this method will check *type_to_bind_to* is an instance of
        :class:`type`, and that you are not attempting to bind a type to
        itself.
    
    .. method:: to_name(name)
    
        Bind the key to a name. Whenever the injector attempts to get an instance
        associated with the key, it will attempt to inject the given type.
        Equivalent to calling ``to_provider(lambda injector: injector.get(name))``,
        except that this method will check *name* is an instance of
        :class:`basestring`, and that you are not attempting to bind a name to
        itself.
