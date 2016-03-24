Zuice: dependency injection for Python
======================================

Zuice is a library for dependency injection in Python.

Example
-------

.. code-block:: python

    import zuice

    class BlogPostLister(zuice.Base):
        _fetcher = zuice.dependency(BlogPostFetcher)

        def all(self):
            return ", ".join(post.name for post in self._fetcher.fetch_all())

    bindings = zuice.Bindings()
    bindings.bind(BlogPostFetcher).to_instance(blog_post_fetcher)

    injector = zuice.Injector(bindings)
    assert injector.get(BlogPostFetcher) is blog_post_fetcher
    injector.get(BlogPostLister) # constructs BlogPostLister using the bound instance of BlogPostFetcher

Usage
-----

The high-level usage overview is:

* Create an instance of ``zuice.Bindings``.

* Add providers to the bindings for cases where Zuice cannot
  automatically infer how to retrieve a value associated with a key.

* Create an instance of ``zuice.Injector`` using these bindings.

* Call ``injector.get(key)`` to retrieve the value associated with ``key``.

Value retrieval
---------------

When ``injector.get(key)`` is called,
either explicitly by the user or while trying to resolve other dependencies,
Zuice will try to retrieve the associated value in one of several ways,
depending on the value of ``key``:

* If a provider for ``key`` has been explicitly bound,
  use that provider.
  
* If ``key`` is an instance of ``zuice.Base``,
  create an instance of ``key`` by injecting its dependencies.

* If ``key`` is a type whose ``__init__`` method takes no arguments,
  call ``key()``.

Bindings
--------

Constants
~~~~~~~~~

Keys can be bound to specific values. For instance:

.. code-block:: python

    bindings = zuice.Bindings()
    bindings.bind(key).to_instance(value)
    injector = zuice.Injector(bindings)
    assert injector.get(key) is value
    
Each time ``injector.get(key)`` is called,
``value`` will always be returned.

Types
~~~~~

Keys can be bound to types. For instance:

.. code-block:: python

    bindings = zuice.Bindings()
    bindings.bind(CookieStore).to_type(RedisCookieStore)
    injector = zuice.Injector(bindings)

Calling ``injector.get(CookieStore)`` will return the same value as calling
``injector.get(RedisCookieStore)``.
However, by calling ``injector.get(CookieStore)``, you avoid relying on
a specific implementation of a cookie store.
If you decide you want to use ``PostgresCookieStore`` at a later date,
you only have to update the bindings rather than all the places that use a cookie store.

Providers
~~~~~~~~~

Keys can be bound to providers.
A provider is a function that takes an injector as its argument,
and returns a value.
For instance:

.. code-block:: python

    bindings = zuice.Bindings()
    bindings.bind(CookieStore).to_provider(lambda injector: injector.get(RedisCookieStore))
    
In most cases, using other methods of binding should suffice.
In this case, using ``to_type`` would be preferred.
