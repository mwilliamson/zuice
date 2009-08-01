import unittest

from zuice import AlreadyBoundException
from zuice import Bindings
from zuice import Injector
from zuice import InvalidBindingException
from zuice import NoSuchBindingException
from zuice import inject_by_name
from zuice import inject_by_type
from zuice import inject_with

class TestInjectorBinding(unittest.TestCase):
    class Apple(object):
        pass
    
    def test_key_in_bindings_if_key_has_been_bound(self):
        Apple = self.Apple
        apple = Apple()
        bindings = Bindings()
        bindings.bind("apple").to_instance(apple)
        
        self.assertTrue("apple" in bindings)
        self.assertTrue("banana" not in bindings)
    
    def test_bind_type_to_instance(self):
        Apple = self.Apple
        apple = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_instance(apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_type(Apple) is apple)
    
    def test_bind_type_raises_exception_if_key_is_not_a_type(self):
        bindings = Bindings()
        self.assertRaises(InvalidBindingException, lambda: bindings.bind_type("apple"))
    
    def test_bind_name_raises_exception_if_key_is_not_a_string(self):
        Apple = self.Apple
        bindings = Bindings()
        self.assertRaises(InvalidBindingException, lambda: bindings.bind_name(Apple))
    
    def test_bind_name_to_instance(self):
        Apple = self.Apple
        apple = Apple()
        bindings = Bindings()
        bindings.bind_name("apple").to_instance(apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_name("apple") is apple)
        
    def test_bind_type_to_provider(self):
        Apple = self.Apple
        apple = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_provider(lambda x: apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_type(Apple) is apple)
    
    def test_get_can_get_by_type_and_name(self):
        Apple = self.Apple
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
        bindings.bind("apple").to_instance(self.Apple())
        injector = Injector(bindings)
        self.assertRaises(TypeError, lambda: injector.get_from_type("apple"))
        
    def test_get_from_name_raises_exception_if_key_is_not_of_correct_type(self):
        bindings = Bindings()
        bindings.bind(self.Apple).to_instance(self.Apple())
        injector = Injector(bindings)
        self.assertRaises(TypeError, lambda: injector.get_from_name(self.Apple))
        
    def test_get_raises_exception_if_key_is_not_of_correct_type(self):
        injector = Injector(Bindings())
        self.assertRaises(NoSuchBindingException, lambda: injector.get(22))
        
    def test_bind_can_bind_names_and_types(self):
        Apple = self.Apple
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
    
    def test_bind_raises_exception_if_using_the_wrong_type_to_bind(self):
        bindings = Bindings()
        self.assertRaises(InvalidBindingException, lambda: bindings.bind(22))
    
    class Donkey(object):
        def __init__(self, legs):
            pass
    
    def test_get_from_type_throws_exception_if_no_such_binding_exists(self):
        injector = Injector(Bindings())
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_type(self.Donkey))
        
        donkey = self.Donkey(4)
        bindings = Bindings()
        bindings.bind_type(self.Donkey).to_provider(lambda x: donkey)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_type(self.Donkey) is donkey)
        
    def test_get_from_name_throws_exception_if_no_such_binding_exists(self):
        Apple = self.Apple
        
        injector = Injector(Bindings())
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_name("apple"))
        
        apple = Apple()
        bindings = Bindings()
        bindings.bind_name("apple").to_provider(lambda x: apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_name("apple") is apple)
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_name("banana"))
    
    def test_changing_bindings_after_creating_injector_does_not_change_injector(self):
        Apple = self.Apple
        apple = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_provider(lambda x: apple)
        
        injector = Injector(bindings)
        bindings.bind_type(Apple).to_provider(lambda: None)
        self.assertTrue(injector.get_from_type(Apple) is apple)
        
    def test_cannot_bind_using_the_same_binder_more_than_once(self):
        Apple = self.Apple
        apple = Apple()
        bindings = Bindings()
        binder = bindings.bind_type(Apple)
        binder.to_provider(lambda: apple)
        self.assertRaises(AlreadyBoundException, lambda: binder.to_provider(lambda: apple))

class Apple(object):
    pass
    
class Banana(object):
    pass
        
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

    class BasketByType(object):
        @inject_by_type(Apple, Banana)
        def __init__(self, apple, banana):
            self.apple = apple
            self.banana = banana
    
    def test_can_inject_constructor_arguments_by_type(self):
        apple_to_inject = Apple()
        banana_to_inject = Banana()
        bindings = Bindings()
        bindings.bind(Apple).to_instance(apple_to_inject)
        bindings.bind(Banana).to_instance(banana_to_inject)
        
        injector = Injector(bindings)
        basket = injector.get(self.BasketByType)
        self.assertTrue(basket.apple is apple_to_inject)
        self.assertTrue(basket.banana is banana_to_inject)
        
    class BasketWith(object):
        @inject_with(Apple, "banana")
        def __init__(self, apple, banana):
            self.apple = apple
            self.banana = banana
    
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
    
    def test_cannot_bind_type_to_itself(self):
        bindings = Bindings()
        self.assertRaises(TypeError, lambda: bindings.bind(Apple).to_type(Apple))
    
    def test_bind_to_type_only_accepts_types(self):
        bindings = Bindings()
        self.assertRaises(TypeError, lambda: bindings.bind("banana").to_type("apple"))

    def test_can_bind_to_names(self):
        apple_to_inject = Apple()
        bindings = Bindings()
        bindings.bind("apple").to_instance(apple_to_inject)
        bindings.bind("another_apple").to_name("apple")
        
        injector = Injector(bindings)
        self.assertTrue(injector.get("another_apple") is apple_to_inject)
    
    def test_cannot_bind_name_to_itself(self):
        bindings = Bindings()
        self.assertRaises(TypeError, lambda: bindings.bind("apple").to_name("apple"))
    
    def test_bind_to_name_only_accepts_strings(self):
        bindings = Bindings()
        self.assertRaises(TypeError, lambda: bindings.bind("banana").to_name(Banana))
    
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
    
    def test_must_use_annotation_to_allow_method_injection(self):
        bindings = Bindings()
        apple = Apple()
        banana = Banana()
        bindings.bind("apple").to_instance(apple)
        bindings.bind("banana").to_instance(banana)
        foo = self.Foo()
        
        injector = Injector(bindings)
        self.assertRaises(NoSuchBindingException, lambda: injector.call(foo.baz))
    
    def test_can_call_methods_with_no_arguments(self):
        injector = Injector(Bindings())
        foo = self.Foo()
        self.assertEquals(20, injector.call(foo.no_args))
    
if __name__ == '__main__':
    unittest.main()
