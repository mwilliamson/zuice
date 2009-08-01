import unittest

from zuice import AlreadyBoundException
from zuice import Bindings
from zuice import Injector
from zuice import InvalidBindingException
from zuice import NoSuchBindingException

class TestInjector(unittest.TestCase):
    class Apple(object):
        pass
    
    def test_key_in_bindings_if_key_has_been_bound(self):
        Apple = TestInjector.Apple
        apple = Apple()
        bindings = Bindings()
        bindings.bind("apple").to_instance(apple)
        
        self.assertTrue("apple" in bindings)
        self.assertTrue("banana" not in bindings)
    
    def test_bind_type_to_instance(self):
        Apple = TestInjector.Apple
        apple = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_instance(apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_type(Apple) is apple)
    
    def test_bind_type_raises_exception_if_key_is_not_a_type(self):
        bindings = Bindings()
        self.assertRaises(InvalidBindingException, lambda: bindings.bind_type("apple"))
    
    def test_bind_name_raises_exception_if_key_is_not_a_string(self):
        Apple = TestInjector.Apple
        bindings = Bindings()
        self.assertRaises(InvalidBindingException, lambda: bindings.bind_name(Apple))
    
    def test_bind_name_to_instance(self):
        Apple = TestInjector.Apple
        apple = Apple()
        bindings = Bindings()
        bindings.bind_name("apple").to_instance(apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_name("apple") is apple)
        
    def test_bind_type_to_provider(self):
        Apple = TestInjector.Apple
        apple = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_provider(lambda: apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_type(Apple) is apple)
    
    def test_get_can_get_by_type_and_name(self):
        Apple = TestInjector.Apple
        apple_by_type = Apple()
        apple_by_name = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_instance(apple_by_type)
        bindings.bind_name("apple").to_instance(apple_by_name)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get(Apple) is apple_by_type)
        self.assertTrue(injector.get("apple") is apple_by_name)
        
    def test_get_raises_exception_if_key_is_not_of_correct_type(self):
        injector = Injector(Bindings())
        self.assertRaises(NoSuchBindingException, lambda: injector.get(22))
        
    def test_bind_can_bind_names_and_types(self):
        Apple = TestInjector.Apple
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
    
    def test_get_from_type_throws_exception_if_no_such_binding_exists(self):
        Apple = TestInjector.Apple
        
        injector = Injector(Bindings())
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_type(Apple))
        
        apple = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_provider(lambda: apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_type(Apple) is apple)
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_type(int))
        
    def test_get_from_name_throws_exception_if_no_such_binding_exists(self):
        Apple = TestInjector.Apple
        
        injector = Injector(Bindings())
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_name("apple"))
        
        apple = Apple()
        bindings = Bindings()
        bindings.bind_name("apple").to_provider(lambda: apple)
        
        injector = Injector(bindings)
        self.assertTrue(injector.get_from_name("apple") is apple)
        self.assertRaises(NoSuchBindingException, lambda: injector.get_from_name("banana"))
    
    def test_changing_bindings_after_creating_injector_does_not_change_injector(self):
        Apple = TestInjector.Apple
        apple = Apple()
        bindings = Bindings()
        bindings.bind_type(Apple).to_provider(lambda: apple)
        
        injector = Injector(bindings)
        bindings.bind_type(Apple).to_provider(lambda: None)
        self.assertTrue(injector.get_from_type(Apple) is apple)
        
    def test_cannot_bind_using_the_same_binder_more_than_once(self):
        Apple = TestInjector.Apple
        apple = Apple()
        bindings = Bindings()
        binder = bindings.bind_type(Apple)
        binder.to_provider(lambda: apple)
        self.assertRaises(AlreadyBoundException, lambda: binder.to_provider(lambda: apple))
        
if __name__ == '__main__':
    unittest.main()
