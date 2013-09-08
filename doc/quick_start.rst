Quick Start
===========

Let's say that we have a :class:`PriceCalculator` class that works out the prices
of various commodities using a :class:`DatabasePriceFetcher`::

    class PriceCalculator(object):
        def __init__(self):
            self._price_fetcher = DatabasePriceFetcher()
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number
            
So we could, for instance, find the price of 10 apples using 
``price_calculator.price_of(apples, 10)``.

We can use an :class:`~zuice.Injector` to construct a :class:`PriceCalculator`
for us since its constructor takes no arguments::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    injector = Injector(bindings)
    price_calculator = injector.get(PriceCalculator)
    
    price = price_calculator.price_of(apples, 10)

Since :class:`~zuice.Injector` can construct a :class:`PriceCalculator`, we
say that the type :class:`PriceCalculator` is injectable.

However, we might decide that we want to pass in a :class:`DatabasePriceFetcher` instead
of constructing it ourselves -- for instance, this makes the class more easily
tested.

We rewrite :class:`PriceCalcuator` as::

    class PriceCalculator(object):
        def __init__(self, price_fetcher):
            self._price_fetcher = price_fetcher
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number

Zuice can no longer construct an instance of :class:`PriceCalculator` for us
-- it does not know how to inject the argument ``price_fetcher``.

Binding instances
^^^^^^^^^^^^^^^^^

The first solution is to manually construct an instance of :class:`PriceCalculator`,
and bind this instance to the type::

    from zuice import Injector
    from zuice import Bindings

    # Assume we've already constructed an instance of PriceCalculator as price_calculator
    bindings = Bindings()
    bindings.bind(PriceCalculator).to_instance(price_calculator)
    injector = Injector(bindings)
    
    injector.get(PriceCalculator) # This returns the same instance of PriceCalculator i.e. price_calculator
    
However, having to construct instances for every type we want to be able to
inject is tedious. Fortunately, we can instead tell Zuice how to inject the
argument ``price_fetcher``.

Binding types
^^^^^^^^^^^^^

We can tell Zuice what type ``price_fetcher`` is using the
:func:`~zuice.inject_with` decorator::

    from zuice import inject_with

    class PriceCalculator(object):
        @inject_with(DatabasePriceFetcher)
        def __init__(self, price_fetcher):
            self._price_fetcher = price_fetcher
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number

:func:`~zuice.inject_with` matches up the given types with the positional arguments.
So, the first type listed is matched up with the first argument -- in this case,
the first type, ``DatabasePriceFetcher``, is matched up with the first argument, ``price_fetcher``.
If there was a second type listed, it would be matched up with the second argument,
and so on.

:func:`~zuice.inject_with` also allows the type of arguments to be specified
using keyword arguments::

    from zuice import inject_with

    class PriceCalculator(object):
        @inject_with(price_fetcher=DatabasePriceFetcher)
        def __init__(self, price_fetcher):
            self._price_fetcher = price_fetcher
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number
            
Using :func:`~zuice.inject_with` in either fashion now allows us to inject
:class:`PriceCalculator`, assuming that :class:`DatabasePriceFetcher` is already
injectable::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    injector = Injector(bindings)
    
    injector.get(PriceCalculator) # This returns a new instance of PriceCalculator
    
This method has the disadvantage that we have now bound :class:`PriceCalculator`
to a specific implementation. What if we wanted to use another class that
behaves in the same manner as :class:`DatabasePriceFetcher`?

One solution is to define a generic type :class:`PriceFetcher`. This might be
as simple as::

    class PriceFetcher(object):
        pass

We then write :class:`PriceCalculator` as::

    from zuice import inject_with

    class PriceCalculator(object):
        @inject_with(price_fetcher=PriceFetcher)
        def __init__(self, price_fetcher):
            self._price_fetcher = price_fetcher
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number
    
Finally, to inject a :class:`PriceCalculator`::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    bindings.bind(PriceFetcher).to_type(DatabasePriceFetcher)
    injector = Injector(bindings)
    price_calculator = injector.get(PriceCalculator)
    
    price = price_calculator.price_of(apples, 10)

Now, whenever a :class:`PriceFetcher` needs to be injected, Zuice will inject a
:class:`DatabasePriceFetcher`. If we decide to use a different implementation,
then we can simple change the binding in this one location.

Binding names
^^^^^^^^^^^^^

In addition to binding types, Zuice allows names to be bound. For instance,
we could write :class:`PriceCalculator` as::

    from zuice import inject_with

    class PriceCalculator(object):
        @inject_with(price_fetcher='price_fetcher')
        def __init__(self, price_fetcher):
            self._price_fetcher = price_fetcher
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number

In order to inject the argument ``price_fetcher``, Zuice will now look up the string
``'price_fetcher'``, rather than the type :class:`PriceFetcher`. We therefore
need to bind ``'price_fetcher'``::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    bindings.bind('price_fetcher').to_type(PriceFetcher)
    bindings.bind(PriceFetcher).to_type(DatabasePriceFetcher)
    injector = Injector(bindings)
    price_calculator = injector.get(PriceCalculator)
    
    price = price_calculator.price_of(apples, 10)

So what happens when we try and inject :class:`PriceCalculator`? It uses
the :func:`~zuice.inject_with` decorator to determine that the argument
``price_fetcher`` must be injected using the name ``'price_fetcher'``. It then
looks up in the bindings what name ``'price_fetcher'`` is bound to -- in this
case, it is bound to :class:`PriceFetcher`.

Zuice then checks what :class:`PriceFetcher` is bound to -- in this case,
:class:`DatabasePriceFetcher`. Since :class:`DatabasePriceFetcher` is not bound
to anything, Zuice will attempt to construct a new instance of :class:`DatabasePriceFetcher`.
This instance is then passed in for the argument ``price_fetcher``.

If we wanted, we could have bound the name ``'price_fetcher'`` directly to
the type :class:`DatabaseFetcher`::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    bindings.bind('price_fetcher').to_type(DatabasePriceFetcher)
    injector = Injector(bindings)
    price_calculator = injector.get(PriceCalculator)
    
    price = price_calculator.price_of(apples, 10)
    
Note how, in this case, the name of the argument exactly matches the name of the
binding we're using. For these cases, the decorator :func:`~zuice.inject_by_name`
can be used::

    from zuice import inject_by_name

    class PriceCalculator(object):
        @inject_by_name
        def __init__(self, price_fetcher):
            self._price_fetcher = price_fetcher
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number

When attempting to inject a :class:`PriceCalculator`, Zuice will lookup the name
``'price_fetcher'`` to inject the argument ``price_fetcher``.

Injecting attributes
^^^^^^^^^^^^^^^^^^^^

Frequently, the arguments in a constructor are assigned to attributes. Therefore,
the decorator :func:`~zuice.inject_attrs` can be used to inject attributes
without having to assign them in the constructor::

    from zuice import inject_attrs

    class PriceCalculator(object):
        @inject_attrs(_price_fetcher=PriceFetcher)
        def __init__(self):
            # Can use self._price_fetcher if we wanted to
            pass
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number

The attributes are assigned before the constructor is used, so these attributes
can be used in the constructor if necessary.

While both :func:`~zuice.inject_with` and :func:`~zuice.inject_by_name` do not
change the signature of the constructor they're used on, :func:`~zuice.inject_attrs`
requires the injected attributes as keyword arguments. So, to manually construct
a :class:`PriceCalculator`, we write::

    price_fetcher = ...
    price_calculator = PriceCalculator(_price_fetcher=price_fetcher)

In the cases where no work is done in the constructor, we can use an alternative
method to inject attributes. Firstly, we have :class:`PriceCalculator` inherit
from :class:`~zuice.Injectable`. We then specify the attributes to be injected
using :func:`~zuice.inject`::

    from zuice import Injectable
    from zuice import inject

    class PriceCalculator(Injectable):
        _price_fetcher = inject(PriceFetcher)
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number

We can manually construct a :class:`PriceCalculator` in the same manner
as above::
    
    price_fetcher = ...
    price_calculator = PriceCalculator(_price_fetcher=price_fetcher)
