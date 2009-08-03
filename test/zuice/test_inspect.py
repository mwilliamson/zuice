import unittest

import zuice.inspect

class SampleObject(object):
    def foo(self, first, second=None, third=30):
        pass
        
    def bar(self, first, second):
        pass

class TestInjectorBinding(unittest.TestCase):
    def test_names_of_methods_are_retrieved(self):
        method_spec = zuice.inspect.get_method_args_spec(SampleObject.foo)
        self.assertEquals('first', method_spec[0].name)
        self.assertEquals('second', method_spec[1].name)
        self.assertEquals('third', method_spec[2].name)
        
    def test_can_determine_whether_an_argument_has_a_default(self):
        method_spec = zuice.inspect.get_method_args_spec(SampleObject.foo)
        self.assertFalse(method_spec[0].has_default)
        self.assertTrue(method_spec[1].has_default)
        self.assertTrue(method_spec[2].has_default)
        
    def test_can_get_defaults_from_arguments(self):
        method_spec = zuice.inspect.get_method_args_spec(SampleObject.foo)
        self.assertEquals(None, method_spec[0].default)
        self.assertEquals(None, method_spec[1].default)
        self.assertEquals(30, method_spec[2].default)
    
    def test_get_method_args_spec_with_no_default_arguments(self):
        method_spec = zuice.inspect.get_method_args_spec(SampleObject.bar)

if __name__ == '__main__':
    unittest.main()
