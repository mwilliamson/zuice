import unittest

import zuice.inspect

class SampleObject(object):
    def foo(self, first, second=None, third=30):
        pass
        
def bar(first, second=None, third=30):
    pass

class TestInspect(unittest.TestCase):
    def test_names_of_method_arguments_are_retrieved(self):
        method_spec = zuice.inspect.get_method_args_spec(SampleObject.foo)
        self.assertEquals(3, len(method_spec))
        self.assertEquals('first', method_spec[0].name)
        self.assertEquals('second', method_spec[1].name)
        self.assertEquals('third', method_spec[2].name)
        
    def test_can_determine_whether_a_method_argument_has_a_default(self):
        method_spec = zuice.inspect.get_method_args_spec(SampleObject.foo)
        self.assertFalse(method_spec[0].has_default)
        self.assertTrue(method_spec[1].has_default)
        self.assertTrue(method_spec[2].has_default)
        
    def test_can_get_defaults_from_method_arguments(self):
        method_spec = zuice.inspect.get_method_args_spec(SampleObject.foo)
        self.assertEquals(None, method_spec[0].default)
        self.assertEquals(None, method_spec[1].default)
        self.assertEquals(30, method_spec[2].default)
    
    def test_names_of_function_arguments_are_retrieved(self):
        function_spec = zuice.inspect.get_function_args_spec(bar)
        self.assertEquals(3, len(function_spec))
        self.assertEquals('first', function_spec[0].name)
        self.assertEquals('second', function_spec[1].name)
        self.assertEquals('third', function_spec[2].name)
        
    def test_can_determine_whether_a_function_argument_has_a_default(self):
        function_spec = zuice.inspect.get_function_args_spec(bar)
        self.assertFalse(function_spec[0].has_default)
        self.assertTrue(function_spec[1].has_default)
        self.assertTrue(function_spec[2].has_default)
        
    def test_can_get_defaults_from_function_arguments(self):
        function_spec = zuice.inspect.get_function_args_spec(bar)
        self.assertEquals(None, function_spec[0].default)
        self.assertEquals(None, function_spec[1].default)
        self.assertEquals(30, function_spec[2].default)

    def test_get_arg_specs_only_removes_first_argument_if_passed_function_is_method(self):
        method_spec = zuice.inspect.get_args_spec(SampleObject.foo)
        self.assertEquals(3, len(method_spec))
        function_spec = zuice.inspect.get_args_spec(bar)
        self.assertEquals(3, len(function_spec))
