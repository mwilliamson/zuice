from nose.tools import assert_raises

from zuice.bindings import AlreadyBoundException
from zuice.bindings import Bindings

class Apple(object):
    pass

def test_key_in_bindings_if_key_has_been_bound():
    apple = Apple()
    bindings = Bindings()
    bindings.bind("apple").to_instance(apple)
    
    assert "apple" in bindings
    assert "banana" not in bindings

def test_bind_type_raises_exception_if_key_is_not_a_type():
    bindings = Bindings()
    assert_raises(TypeError, lambda: bindings.bind_type("apple"))

def test_bind_name_raises_exception_if_key_is_not_a_string():
    bindings = Bindings()
    assert_raises(TypeError, lambda: bindings.bind_name(Apple))

def test_bind_raises_exception_if_using_the_wrong_type_to_bind():
    bindings = Bindings()
    assert_raises(TypeError, lambda: bindings.bind(22))
    
def test_cannot_bind_using_the_same_binder_more_than_once():
    apple = Apple()
    bindings = Bindings()
    binder = bindings.bind_type(Apple)
    binder.to_provider(lambda: apple)
    assert_raises(AlreadyBoundException, lambda: binder.to_provider(lambda: apple))

def test_cannot_bind_the_same_name_or_type_more_than_once():
    apple = Apple()
    bindings = Bindings()
    bindings.bind('apple').to_instance(apple)
    assert_raises(AlreadyBoundException, lambda: bindings.bind('apple'))
    assert_raises(AlreadyBoundException, lambda: bindings.bind_name('apple'))

def test_cannot_bind_type_to_itself():
    bindings = Bindings()
    assert_raises(TypeError, lambda: bindings.bind(Apple).to_type(Apple))

def test_bind_to_type_only_accepts_types():
    bindings = Bindings()
    assert_raises(TypeError, lambda: bindings.bind("banana").to_type("apple"))

def test_cannot_bind_name_to_itself():
    bindings = Bindings()
    assert_raises(TypeError, lambda: bindings.bind("apple").to_name("apple"))

def test_bind_to_name_only_accepts_strings():
    bindings = Bindings()
    assert_raises(TypeError, lambda: bindings.bind("apple").to_name(Apple))
