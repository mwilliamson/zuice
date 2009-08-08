import unittest

from zuice.bindings import AlreadyBoundException
from zuice.bindings import Bindings
from zuice.bindings import InvalidBindingException

class Apple(object):
    pass

class TestBindings(unittest.TestCase):
    def test_key_in_bindings_if_key_has_been_bound(self):
        apple = Apple()
        bindings = Bindings()
        bindings.bind("apple").to_instance(apple)
        
        self.assertTrue("apple" in bindings)
        self.assertTrue("banana" not in bindings)
    
    def test_bind_type_raises_exception_if_key_is_not_a_type(self):
        bindings = Bindings()
        self.assertRaises(InvalidBindingException, lambda: bindings.bind_type("apple"))
    
    def test_bind_name_raises_exception_if_key_is_not_a_string(self):
        bindings = Bindings()
        self.assertRaises(InvalidBindingException, lambda: bindings.bind_name(Apple))
    
    def test_bind_raises_exception_if_using_the_wrong_type_to_bind(self):
        bindings = Bindings()
        self.assertRaises(InvalidBindingException, lambda: bindings.bind(22))
        
    def test_cannot_bind_using_the_same_binder_more_than_once(self):
        apple = Apple()
        bindings = Bindings()
        binder = bindings.bind_type(Apple)
        binder.to_provider(lambda: apple)
        self.assertRaises(AlreadyBoundException, lambda: binder.to_provider(lambda: apple))
    

if __name__ == '__main__':
    unittest.main()

    
