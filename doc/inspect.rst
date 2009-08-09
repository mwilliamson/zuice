:mod:`zuice.inspect`
====================

.. module:: zuice.inspect

This module is a wrapper around Python's :mod:`inspect` module. This was designed
to meet the requirements in Zuice for inspecting functions and methods, and therefore
behaves differently from :mod:`inspect`.

.. function:: get_args_spec(function)

    Gets the names and default values of a function's arguments. A list of :class:`Argument`
    objects are returned. At present, this means that information about varargs is discarded.
    
    If the first argument of a function is `self`, it is assumed that the function is
    actually a method, and so the first argument is discarded. When a decorator is
    used on a method, the method has not yet been bound to the class, and therefore
    appears to be a function -- that is, :func:`inspect.ismethod` returns :keyword:`False`.
    Therefore, the name of the first argument is the best guess.
    
.. class:: Argument

    .. attribute:: name
    
        The name of the argument.
    
    .. attribute:: has_default
    
        :keyword:`True` if this argument has a default value, :keyword:`False` otherwise.
    
    .. attribute:: default
    
        The default value of this argument. Note that if the value of this attribute
        is :keyword:`None`, there are two possibilities -- either this argument
        has no default value, or the default value is :keyword:`None`. Use 
        :attr:`has_default` to differentiate between the two cases.
