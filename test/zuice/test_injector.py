import unittest
from nose.tools import assert_raises

from zuice.bindings import Bindings
from zuice import Injector
from zuice import NoSuchBindingException
from zuice import inject_by_name
from zuice import inject_with
from zuice import inject_attrs

from zuice import inject
from zuice import Injectable

class Apple(object):
    pass
    
default_apple = Apple()
    
class Banana(object):
    pass
    
class TestInjectorBinding(unittest.TestCase):
    def test_bind_type_to_instance(self):
        apple = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_instance(apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_type(Apple) is apple)
    
    def test_bind_name_to_instance(self):
        apple = Apple()
        bindings = Bindings()
        bindings.bind_name("apple").to_instance(apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_name("apple") is apple)
        
    def test_bind_type_to_provider(self):
        apple = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_provider(lambda: apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_type(Apple) is apple)
    
    def test_get_can_get_by_type_and_name(self):
        apple_by_type = Apple()
        apple_by_name = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_instance(apple_by_type)
        bindings.bind_name("apple").to_instance(apple_by_name)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get(Apple) is apple_by_type)
        self.assertTrue(injector.get("apple") is apple_by_name)
        
    def test_get_from_type_raises_exception_if_key_is_not_type(self):
        bindings = Bindings()
        bindings.bind("apple").to_instance(Apple())
        injector = Injector(bindings)
        self.assertRaises(TypeError, lambda: injector.get_from_type("apple"))
        
    def test_get_from_name_raises_exception_if_key_is_not_of_correct_type(self):
        bindings = Bindings()
        bindings.bind(Apple).to_instance(Apple())
        injector = Injector(bindings)
        self.assertRaises(TypeError, lambda: injector.get_from_name(Apple))
        
    def test_get_raises_exception_if_key_is_not_of_correct_type(self):
        injector = Injector(Bindings())
        self.assertRaises(NoSuchBindingException, lambda: injector.get(22))
        
    def test_bind_can_bind_names_and_types(self):
        apple_by_type = Apple()
        apple_by_name = Apple()
        bindings = Bindings()
        bindings.bind(Apple).to_instance(apple_by_type)
        bindings.bind("apple").to_instance(apple_by_name)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get(Apple) is apple_by_type)
        self.assertTrue(injector.get_from_type(Apple) is apple_by_type)
        self.assertTrue(injector.get("apple") is apple_by_name)
        self.assertTrue(injector.get_from_name("apple") is apple_by_name)
    
    class Donkey(object):
        def __init__(self, legs):
            pass
    
    def test_get_from_type_throws_exception_if_no_such_binding_exists(self):
        injector = Injector(Bindings())
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_type(self.Donkey))
        
        donkey = self.Donkey(4)
        bindings = Bindings()
        bindings.bind_type(self.Donkey).to_provider(lambda: donkey)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_type(self.Donkey) is donkey)
        
    def test_get_from_name_throws_exception_if_no_such_binding_exists(self):
        injector = Injector(Bindings())
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_name("apple"))
        
        apple = Apple()
        bindings = Bindings()
        bindings.bind_name("apple").to_provider(lambda: apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_name("apple") is apple)
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_name("banana"))
    
    def test_changing_bindings_after_creating_injector_does_not_change_injector(self):
        bindings = Bindings()
        injector = Injector(bindings)
        bindings.bind("apple").to_instance(Apple())
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_name("apple"))
    
class TestInjector(unittest.TestCase):
    class BasketByName(object):
        @inject_by_name
        def __init__(self, apple, banana):
            self.apple = apple
            self.banana = banana
            
    def test_can_inject_constructor_arguments_by_name(self):
        apple_to_inject = Apple()
        banana_to_inject = Banana()
        bindings = Bindings()
        bindings.bind("apple").to_instance(apple_to_inject)
        bindings.bind("banana").to_instance(banana_to_inject)
        
        injector = Injector(bindings)
        basket = injector.get(self.BasketByName)
        self.assertTrue(basket.apple is apple_to_inject)
        self.assertTrue(basket.banana is banana_to_inject)
        
    class BasketWith(object):
        @inject_with(Apple, "banana")
        def __init__(self, apple, banana, foo=10):
            self.apple = apple
            self.banana = banana
            self.foo = foo
    
    def test_can_inject_constructor_arguments_by_type(self):
        apple_to_inject = Apple()
        banana_to_inject = Banana()
        bindings = Bindings()
        bindings.bind(Apple).to_instance(apple_to_inject)
        bindings.bind("banana").to_instance(banana_to_inject)
        
        injector = Injector(bindings)
        basket = injector.get(self.BasketWith)
        self.assertTrue(basket.apple is apple_to_inject)
        self.assertTrue(basket.banana is banana_to_inject)
        self.assertEquals(10, basket.foo)
    
    class BasketWithNamed(object):
        @inject_with(apple=Apple, banana="banana")
        def __init__(self, banana, another_apple=default_apple, apple=default_apple):
            self.apple = apple
            self.another_apple = another_apple
            self.banana = banana
    
    def test_can_inject_with_using_named_parameters(self):
        apple_to_inject = Apple()
        banana_to_inject = Banana()
        bindings = Bindings()
        bindings.bind(Apple).to_instance(apple_to_inject)
        bindings.bind("banana").to_instance(banana_to_inject)
        
        injector = Injector(bindings)
        basket = injector.get(self.BasketWithNamed)
        self.assertTrue(basket.apple is apple_to_inject)
        self.assertTrue(basket.another_apple is default_apple)
        self.assertTrue(basket.banana is banana_to_inject)
    
    class BasketWithKwargs(object):
        @inject_with(apple=Apple, banana="banana")
        def __init__(self, apple, **kwargs):
            self.apple = apple
            self.kwargs = kwargs
    
    def test_keys_without_matching_parameters_are_used_as_keyword_arguments(self):
        apple_to_inject = Apple()
        banana_to_inject = Banana()
        bindings = Bindings()
        bindings.bind(Apple).to_instance(apple_to_inject)
        bindings.bind("banana").to_instance(banana_to_inject)
        
        injector = Injector(bindings)
        basket = injector.get(self.BasketWithKwargs)
        self.assertTrue(basket.apple is apple_to_inject)
        self.assertTrue(basket.kwargs['banana'] is banana_to_inject)
    
    class BasketWithUnspecified(object):
        @inject_with(banana="banana")
        def __init__(self, banana, apple=default_apple):
            self.apple = apple
            self.banana = banana
    
    def test_inject_with_uses_argument_name_after_named_parameter_and_before_defaults(self):
        apple_to_inject = Apple()
        banana_to_inject = Banana()
        bindings = Bindings()
        bindings.bind("apple").to_instance(apple_to_inject)
        bindings.bind("banana").to_instance(banana_to_inject)
        
        injector = Injector(bindings)
        basket = injector.get(self.BasketWithUnspecified)
        self.assertTrue(basket.apple is apple_to_inject)
        self.assertTrue(basket.banana is banana_to_inject)
    
    def test_overspecifying_argument_results_in_exception(self):
        def define_overspecified():
            class Overspecified(object):
                @inject_with("banana", banana="banana")
                def __init__(self, banana):
                    pass
        self.assertRaises(TypeError, define_overspecified)
    
    class Coconut(object):
        def __init__(self):
            self.x = 10
    
    class Durian(object):
        pass
        
    def test_can_inject_class_with_no_constructor_arguments(self):
        injector = Injector(Bindings())
        coconut = injector.get(self.Coconut)
        self.assertEquals(10, coconut.x)
        injector.get(self.Durian)
    
    def test_can_bind_names_to_injectable_types(self):
        apple_to_inject = Apple()
        banana_to_inject = Banana()
        bindings = Bindings()
        bindings.bind(Apple).to_instance(apple_to_inject)
        bindings.bind(Banana).to_instance(banana_to_inject)
        bindings.bind("banana").to_type(Banana)
        bindings.bind("basket").to_type(self.BasketWith)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get("banana") is banana_to_inject)
        
        basket = injector.get("basket")
        self.assertTrue(basket.apple is apple_to_inject)
        self.assertTrue(basket.banana is banana_to_inject)

    def test_can_bind_to_names(self):
        apple_to_inject = Apple()
        bindings = Bindings()
        bindings.bind("apple").to_instance(apple_to_inject)
        bindings.bind("another_apple").to_name("apple")
        
        injector = Injector(bindings)
        self.assertTrue(injector.get("another_apple") is apple_to_inject)
    
    def test_uses_bindings_before_injection(self):
        bindings = Bindings()
        basket = self.BasketWith(Apple(), Banana())
        bindings.bind(self.BasketWith).to_instance(basket)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get(self.BasketWith) is basket)
    
    class Foo(object):
        @inject_by_name
        def bar(self, apple, banana):
            self.apple = apple
            self.banana = banana
            return banana
            
        def baz(self, apple, banana):
            pass
            
        def no_args(self):
            return 20
    
    def test_can_inject_methods(self):
        bindings = Bindings()
        apple = Apple()
        banana = Banana()
        bindings.bind("apple").to_instance(apple)
        bindings.bind("banana").to_instance(banana)
        foo = self.Foo()
        
        injector = Injector(bindings)
        returned_value = injector.call(foo.bar)
        
        self.assertTrue(returned_value is banana)
        self.assertTrue(foo.apple is apple)
        self.assertTrue(foo.banana is banana)
        
    def test_can_call_methods_with_no_arguments(self):
        injector = Injector(Bindings())
        foo = self.Foo()
        self.assertEquals(20, injector.call(foo.no_args))
    
    def test_inject_by_name_uses_default_arguments_if_no_bindings_can_be_found(self):
        default_banana = Banana()
        
        class DefaultArguments(object):
            @inject_by_name
            def __init__(self, apple, banana=default_banana, another_banana=default_banana):
                self.apple = apple
                self.banana = banana
                self.another_banana = another_banana
                
        bindings = Bindings()
        apple = Apple()
        banana = Banana()
        bindings.bind("apple").to_instance(apple)
        bindings.bind("another_banana").to_instance(banana)
        
        injector = Injector(bindings)
        injected = injector.get(DefaultArguments)
        self.assertTrue(injected.apple is apple)
        self.assertTrue(injected.banana is default_banana)
        self.assertTrue(injected.another_banana is banana)

    def test_injector_name_is_always_bound_to_injector(self):
        injector = Injector(Bindings())
        self.assertTrue(injector.get('injector') is injector)
        
    def test_injector_class_is_bound_to_injector(self):
        injector = Injector(Bindings())
        self.assertTrue(injector.get(Injector) is injector)
    
def test_inject_by_name_wraps_functions():
    @inject_by_name
    def to_wrap_with_inject_by_name():
        """Docstring"""
        pass
    assert to_wrap_with_inject_by_name.__name__ == 'to_wrap_with_inject_by_name'
    assert to_wrap_with_inject_by_name.__doc__ == 'Docstring'
    
def test_inject_with_wraps_functions():
    @inject_with()
    def to_wrap_with_inject_with():
        """Docstring"""
        pass
    assert to_wrap_with_inject_with.__name__ == 'to_wrap_with_inject_with'
    assert to_wrap_with_inject_with.__doc__ == 'Docstring'

def test_inject_attrs_assigns_the_given_attributes():
    class Foo(object):
        @inject_attrs(_tag_fetcher='tag_fetcher')
        def __init__(self):
            pass
    
    tag_fetcher = {'some': 'object'}
    
    bindings = Bindings()
    bindings.bind("tag_fetcher").to_instance(tag_fetcher)
    injector = Injector(bindings)
    assert injector.get(Foo)._tag_fetcher is tag_fetcher
    
def test_inject_attrs_allows_constructor_arguments_to_be_passed_manually():
    class Foo(object):
        @inject_attrs(_tag_fetcher='tag_fetcher')
        def __init__(self):
            pass
    
    tag_fetcher = {'some': 'object'}
    
    assert Foo(_tag_fetcher=tag_fetcher)._tag_fetcher is tag_fetcher
    
def test_inject_attrs_manually_with_missing_args_raises_type_error():
    class Foo(object):
        @inject_attrs(_tag_fetcher='tag_fetcher', _blog_post_fetcher='post_fetcher')
        def __init__(self):
            pass
    
    tag_fetcher = {'some': 'object'}
    
    assert_raises(TypeError, lambda: Foo(_tag_fetcher=tag_fetcher))

def test_inject_attrs_injecting_manually_with_extra_members_raises_type_error():
    class Foo(object):
        @inject_attrs(_tag_fetcher='tag_fetcher')
        def __init__(self):
            pass
    
    tag_fetcher = {'some': 'object'}
    post_fetcher = {'another': 'object'}
    
    assert_raises(TypeError, lambda: Foo(_tag_fetcher=tag_fetcher, _post_fetcher=post_fetcher))

def test_classes_that_inherit_from_injectable_have_members_injected():
    class Foo(Injectable):
        _tag_fetcher = inject("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    
    bindings = Bindings()
    bindings.bind("tag_fetcher").to_instance(tag_fetcher)
    injector = Injector(bindings)
    assert injector.get(Foo)._tag_fetcher is tag_fetcher

def test_classes_that_inherit_from_injectable_can_be_passed_constructor_arguments_manually():
    class Foo(Injectable):
        _tag_fetcher = inject("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    
    assert Foo(_tag_fetcher=tag_fetcher)._tag_fetcher is tag_fetcher

def test_missing_constructor_arguments_in_injectable_raises_type_error():
    class Foo(Injectable):
        _tag_fetcher = inject("tag_fetcher")
        _blog_post_fetcher = inject('post_fetcher')
    
    tag_fetcher = {'some': 'object'}
    
    assert_raises(TypeError, lambda: Foo(_tag_fetcher=tag_fetcher))

def test_injectable_injecting_manually_with_extra_members_raises_type_error():
    class Foo(Injectable):
        _tag_fetcher = inject("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    post_fetcher = {'another': 'object'}
    
    assert_raises(TypeError, lambda: Foo(_tag_fetcher=tag_fetcher, _post_fetcher=post_fetcher))

def test_injectable_injecting_positional_arguments_raises_type_error():
    class Foo(Injectable):
        _tag_fetcher = inject('tag_fetcher')
        
    tag_fetcher = {'some': 'object'}
    
    assert_raises(TypeError, lambda: Foo(tag_fetcher))
    
