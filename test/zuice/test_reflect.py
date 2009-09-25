import zuice.reflect

from nose.tools import assert_equals

class SampleObject(object):
    def foo(self, first, second=None, third=30):
        pass

def test_names_of_method_arguments_are_retrieved():
    method_spec = zuice.reflect.get_args_spec(SampleObject.foo)
    assert_equals(3, len(method_spec))
    assert_equals('first', method_spec[0].name)
    assert_equals('second', method_spec[1].name)
    assert_equals('third', method_spec[2].name)
    
def test_can_determine_whether_a_method_argument_has_a_default():
    method_spec = zuice.reflect.get_args_spec(SampleObject.foo)
    assert not method_spec[0].has_default
    assert method_spec[1].has_default
    assert method_spec[2].has_default
    
def test_can_get_defaults_from_method_arguments():
    method_spec = zuice.reflect.get_args_spec(SampleObject.foo)
    assert_equals(None, method_spec[0].default)
    assert_equals(None, method_spec[1].default)
    assert_equals(30, method_spec[2].default)

def bar(first, second=None, third=30):
    pass
        
def test_names_of_function_arguments_are_retrieved():
    function_spec = zuice.reflect.get_args_spec(bar)
    assert_equals(3, len(function_spec))
    assert_equals('first', function_spec[0].name)
    assert_equals('second', function_spec[1].name)
    assert_equals('third', function_spec[2].name)
    
def test_can_determine_whether_a_function_argument_has_a_default():
    function_spec = zuice.reflect.get_args_spec(bar)
    assert not function_spec[0].has_default
    assert function_spec[1].has_default
    assert function_spec[2].has_default
    
def test_can_get_defaults_from_function_arguments():
    function_spec = zuice.reflect.get_args_spec(bar)
    assert_equals(None, function_spec[0].default)
    assert_equals(None, function_spec[1].default)
    assert_equals(30, function_spec[2].default)

def test_get_arg_specs_only_removes_first_argument_if_passed_function_is_method():
    method_spec = zuice.reflect.get_args_spec(SampleObject.foo)
    assert_equals(3, len(method_spec))
    function_spec = zuice.reflect.get_args_spec(bar)
    assert_equals(3, len(function_spec))

def noargs():
    pass
    
def test_can_inspect_zero_argument_function():
    function_spec = zuice.reflect.get_args_spec(noargs)
    assert_equals(0, len(function_spec))
