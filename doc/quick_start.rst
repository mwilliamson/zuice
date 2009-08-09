Quick Start
===========

Let's say that we have a ``PriceCalculator`` class that works out the prices
of various commodities using a ``PriceFetcher``::

    class PriceCalculator(object):
        def __init__(self, price_fetcher):
            self._price_fetcher = price_fetcher
            
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number
            
So we could, for instance, find the price of 10 apples using 
``price_calculator.price_of(apples, 10)``.

To get an instance of a ``PriceCalculator``, we need an :class:`~zuice.Injector`, which must be
constructed with a :class:`~zuice.bindings.Bindings`::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    injector = Injector(bindings)
    price_calculator = injector.get(PriceCalculator)

At the moment, this code will fail since ``PriceCalculator`` is not injectable -- 
Zuice does not know what to pass in for the argument ``price_fetcher``. If
``PriceCalculator.__init__`` could be called with no arguments (other than ``self``)
then the call ``injector.get(PriceCalculator)`` would have succeeded -- Zuice would
simply call ``PriceCalculator()``.

The easiest way of rectifying this is to bind the type directly to a given instance::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    bindings.bind(PriceCalculator).to_instance(price_calculator)
    injector = Injector(bindings)
    
This means that ``injector.get(PriceCalculator)`` will always return the same
instance.

The final method of making ``PriceCalculator`` injectable is to mark its constructor
as injectable::

    from zuice import inject_by_name

    class PriceCalculator(object):
        @inject_by_name
        def __init__(self, price_fetcher):
            self._price_fetcher = price_fetcher
            
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number

However, attempting to get a ``PriceCalculator`` will fail since Zuice still
does not know what should be passed in as ``price_fetcher``.

We need some way of binding the argument ``price_fetcher`` to the relevant class. In a
statically typed language, we can use the type of the parameter to determine
what needs to be injected. However, in a dynamically typed language such as
Python, we need an alternative method.

By using :func:`~zuice.inject_by_name`, we are indicating that this binding should
be done by the name of each argument. We therefore need to bind the string
``'price_fetcher'``::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    bindings.bind('price_fetcher').to_type(PriceFetcher)
    injector = Injector(bindings)
    price_calculator = injector.get(PriceCalculator)

Each time Zuice finds an argument called ``price_fetcher``, it will attempt to
inject ``PriceFetcher``. ``PriceFetcher`` may already be injectable if its
constructor takes no arguments. Otherwise, it can be made injectable in the same
manner as ``PriceCalculator``. We could also bind the name directly to an instance::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    bindings.bind('price_fetcher').to_instance(price_fetcher)
    injector = Injector(bindings)
    price_calculator = injector.get(PriceCalculator)

The second method is binding by key, using the decorator :func:`~zuice.inject_with`::

    from zuice import inject_by_name

    class PriceCalculator(object):
        @inject_with(PriceFetcher)
        def __init__(self, price_fetcher):
            self._price_fetcher = price_fetcher
            
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number

We then need to make sure that the ``PriceFetcher`` class is injectable.
    
.. note:: A type is injectable if either:

        * The type's constructor has no required arguments, or
        * The type has already been bound, or
        * The type's constructor has had one of Zuice's injection decorators
          applied to it; either :func:`~zuice.inject_by_name` or :func:`~zuice.inject_with`. Each of the
          type constructor's arguments must also be injectable.

