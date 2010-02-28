from nose.tools import assert_equals
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
    
def test_bind_type_to_instance():
    apple = Apple()
    bindings = Bindings()
    bindings.bind(Apple).to_instance(apple)
    
    injector = Injector(bindings)
    assert injector.get_from_type(Apple) is apple

def test_bind_name_to_instance():
    apple = Apple()
    bindings = Bindings()
    bindings.bind("apple").to_instance(apple)
    
    injector = Injector(bindings)
    assert injector.get("apple") is apple
    
def test_bind_type_to_provider():
    apple = Apple()
    bindings = Bindings()
    bindings.bind(Apple).to_provider(lambda: apple)
    
    injector = Injector(bindings)
    assert injector.get_from_type(Apple) is apple

def test_get_can_get_by_type_and_name():
    apple_by_type = Apple()
    apple_by_name = Apple()
    bindings = Bindings()
    bindings.bind(Apple).to_instance(apple_by_type)
    bindings.bind("apple").to_instance(apple_by_name)
    
    injector = Injector(bindings)
    assert injector.get(Apple) is apple_by_type
    assert injector.get("apple") is apple_by_name
    
def test_get_from_type_raises_exception_if_key_is_not_type():
    bindings = Bindings()
    bindings.bind("apple").to_instance(Apple())
    injector = Injector(bindings)
    assert_raises(TypeError, lambda: injector.get_from_type("apple"))
    
def test_bind_can_bind_names_and_types():
    apple_by_type = Apple()
    apple_by_name = Apple()
    bindings = Bindings()
    bindings.bind(Apple).to_instance(apple_by_type)
    bindings.bind("apple").to_instance(apple_by_name)
    
    injector = Injector(bindings)
    assert injector.get(Apple) is apple_by_type
    assert injector.get_from_type(Apple) is apple_by_type
    assert injector.get("apple") is apple_by_name

def test_get_from_type_throws_exception_if_no_such_binding_exists():
    class Donkey(object):
        def __init__(self, legs):
            pass
        
    injector = Injector(Bindings())
    assert_raises(NoSuchBindingException, lambda: injector.get_from_type(Donkey))
    
    donkey = Donkey(4)
    bindings = Bindings()
    bindings.bind(Donkey).to_provider(lambda: donkey)
    
    injector = Injector(bindings)
    assert injector.get_from_type(Donkey) is donkey
    
def test_get_raises_exception_if_no_such_binding_exists():
    injector = Injector(Bindings())
    assert_raises(NoSuchBindingException, lambda: injector.get("apple"))
    
    apple = Apple()
    bindings = Bindings()
    bindings.bind("apple").to_provider(lambda: apple)
    
    injector = Injector(bindings)
    assert injector.get("apple") is apple
    assert_raises(NoSuchBindingException, lambda: injector.get("banana"))

def test_changing_bindings_after_creating_injector_does_not_change_injector():
    bindings = Bindings()
    injector = Injector(bindings)
    bindings.bind("apple").to_instance(Apple())
    assert_raises(NoSuchBindingException, lambda: injector.get("apple"))
        
def test_can_inject_constructor_arguments_by_name():
    class BasketByName(object):
        @inject_by_name
        def __init__(self, apple, banana):
            self.apple = apple
            self.banana = banana
            
    apple_to_inject = Apple()
    banana_to_inject = Banana()
    bindings = Bindings()
    bindings.bind("apple").to_instance(apple_to_inject)
    bindings.bind("banana").to_instance(banana_to_inject)
    
    injector = Injector(bindings)
    basket = injector.get(BasketByName)
    assert basket.apple is apple_to_inject
    assert basket.banana is banana_to_inject

def test_can_inject_constructor_arguments_by_type():
    class BasketWith(object):
        @inject_with(Apple, "banana")
        def __init__(self, apple, banana, foo=10):
            self.apple = apple
            self.banana = banana
            self.foo = foo
            
    apple_to_inject = Apple()
    banana_to_inject = Banana()
    bindings = Bindings()
    bindings.bind(Apple).to_instance(apple_to_inject)
    bindings.bind("banana").to_instance(banana_to_inject)
    
    injector = Injector(bindings)
    basket = injector.get(BasketWith)
    assert basket.apple is apple_to_inject
    assert basket.banana is banana_to_inject
    assert_equals(10, basket.foo)

def test_can_inject_with_using_named_parameters():
    class BasketWithNamed(object):
        @inject_with(apple=Apple, banana="banana")
        def __init__(self, banana, another_apple=default_apple, apple=default_apple):
            self.apple = apple
            self.another_apple = another_apple
            self.banana = banana
            
    apple_to_inject = Apple()
    banana_to_inject = Banana()
    bindings = Bindings()
    bindings.bind(Apple).to_instance(apple_to_inject)
    bindings.bind("banana").to_instance(banana_to_inject)
    
    injector = Injector(bindings)
    basket = injector.get(BasketWithNamed)
    assert basket.apple is apple_to_inject
    assert basket.another_apple is default_apple
    assert basket.banana is banana_to_inject

def test_keys_without_matching_parameters_are_used_as_keyword_arguments():
    class BasketWithKwargs(object):
        @inject_with(apple=Apple, banana="banana")
        def __init__(self, apple, **kwargs):
            self.apple = apple
            self.kwargs = kwargs
            
    apple_to_inject = Apple()
    banana_to_inject = Banana()
    bindings = Bindings()
    bindings.bind(Apple).to_instance(apple_to_inject)
    bindings.bind("banana").to_instance(banana_to_inject)
    
    injector = Injector(bindings)
    basket = injector.get(BasketWithKwargs)
    assert basket.apple is apple_to_inject
    assert basket.kwargs['banana'] is banana_to_inject

def test_inject_with_uses_argument_name_after_named_parameter_and_before_defaults():
    class BasketWithUnspecified(object):
        @inject_with(banana="banana")
        def __init__(self, banana, apple=default_apple):
            self.apple = apple
            self.banana = banana
            
    apple_to_inject = Apple()
    banana_to_inject = Banana()
    bindings = Bindings()
    bindings.bind("apple").to_instance(apple_to_inject)
    bindings.bind("banana").to_instance(banana_to_inject)
    
    injector = Injector(bindings)
    basket = injector.get(BasketWithUnspecified)
    assert basket.apple is apple_to_inject
    assert basket.banana is banana_to_inject

def test_overspecifying_argument_results_in_exception():
    def define_overspecified():
        class Overspecified(object):
            @inject_with("banana", banana="banana")
            def __init__(self, banana):
                pass
                
    assert_raises(TypeError, define_overspecified)

def test_can_inject_class_with_no_constructor_arguments():
    class Coconut(object):
        def __init__(self):
            self.x = 10
            
    injector = Injector(Bindings())
    coconut = injector.get(Coconut)
    assert_equals(10, coconut.x)

def test_can_bind_names_to_injectable_types():
    class Basket(object):
        @inject_with(banana="banana")
        def __init__(self, banana):
            self.banana = banana
            
    banana_to_inject = Banana()
    bindings = Bindings()
    bindings.bind(Banana).to_instance(banana_to_inject)
    bindings.bind("banana").to_type(Banana)
    bindings.bind("basket").to_type(Basket)
    
    injector = Injector(bindings)
    assert injector.get("banana") is banana_to_inject
    
    basket = injector.get("basket")
    assert basket.banana is banana_to_inject

def test_can_bind_to_names():
    apple_to_inject = Apple()
    bindings = Bindings()
    bindings.bind("apple").to_instance(apple_to_inject)
    bindings.bind("another_apple").to_key("apple")
    
    injector = Injector(bindings)
    assert injector.get("another_apple") is apple_to_inject

def test_uses_bindings_before_injection():
    class Basket(object):
        @inject_with(banana="banana")
        def __init__(self, banana):
            self.banana = banana
            
    bindings = Bindings()
    basket = Basket(Banana())
    bindings.bind(Basket).to_instance(basket)
    
    injector = Injector(bindings)
    assert injector.get(Basket) is basket

def test_can_inject_methods():
    class Foo(object):
        def bar(self, apple, banana):
            self.apple = apple
            self.banana = banana
            return banana
    bindings = Bindings()
    apple = Apple()
    banana = Banana()
    bindings.bind("apple").to_instance(apple)
    bindings.bind("banana").to_instance(banana)
    foo = Foo()
    
    injector = Injector(bindings)
    returned_value = injector.call(foo.bar)
    
    assert returned_value is banana
    assert foo.apple is apple
    assert foo.banana is banana
    
def test_can_call_methods_with_no_arguments():
    class Foo(object):
        def no_args(self):
            return 20
    injector = Injector(Bindings())
    foo = Foo()
    assert_equals(20, injector.call(foo.no_args))

def test_inject_by_name_uses_default_arguments_if_no_bindings_can_be_found():
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
    assert injected.apple is apple
    assert injected.banana is default_banana
    assert injected.another_banana is banana

def test_injector_name_is_always_bound_to_injector():
    injector = Injector(Bindings())
    assert injector.get('injector') is injector
    
def test_injector_class_is_bound_to_injector():
    injector = Injector(Bindings())
    assert injector.get(Injector) is injector
    
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

def test_classes_that_inherit_from_injectable_can_be_passed_constructor_arguments_manually_by_name():
    class Foo(Injectable):
        _tag_fetcher = inject("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    
    assert Foo(_tag_fetcher=tag_fetcher)._tag_fetcher is tag_fetcher

def test_classes_that_inherit_from_injectable_can_be_passed_constructor_arguments_manually_by_position():
    class View(Injectable):
        _tag_fetcher = inject("tag_fetcher")
        _post_fetcher = inject("post_fetcher")
    
    tag_fetcher = {'some': 'object'}
    post_fetcher = {'another': 'object'}
    
    view = View(tag_fetcher, post_fetcher)
    assert view._tag_fetcher is tag_fetcher
    assert view._post_fetcher is post_fetcher

def test_injecting_overspecified_arguments_to_injectable_raises_exception():
    class View(Injectable):
        _tag_fetcher = inject("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    
    try:
        view = View(tag_fetcher, _tag_fetcher=tag_fetcher)
        assert False
    except TypeError, e:
        assert_equals(str(e), "Got multiple values for keyword argument '_tag_fetcher'")

def test_injecting_too_many_positional_arguments_to_injectable_raises_exception():
    class View(Injectable):
        _tag_fetcher = inject("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    post_fetcher = {'another': 'object'}
    
    try:
        view = View(tag_fetcher, post_fetcher)
        assert False
    except TypeError, e:
        assert_equals(str(e), "View requires 1 injected member(s) (2 given)")

def test_injectable_injects_attributes_of_sub_classes():
    class Parent(Injectable):
        _tag_fetcher = inject('tag_fetcher')
        
    class Child(Parent):
        _blog_post_fetcher = inject('post_fetcher')

    tag_fetcher = {'some': 'object'}
    post_fetcher = {'another': 'object'}
    
    bindings = Bindings()
    bindings.bind("tag_fetcher").to_instance(tag_fetcher)
    bindings.bind("post_fetcher").to_instance(post_fetcher)
    injector = Injector(bindings)
    child = injector.get(Child)
    
    assert child._tag_fetcher is tag_fetcher
    assert child._blog_post_fetcher is post_fetcher

def test_subclassing_injectable_objects_allows_injected_attributes_to_be_overwritten():
    class Parent(Injectable):
        _fetcher = inject('tag_fetcher')
        
    class Child(Parent):
        _fetcher = inject('post_fetcher')

    post_fetcher = {'another': 'object'}
    
    bindings = Bindings()
    bindings.bind("post_fetcher").to_instance(post_fetcher)
    injector = Injector(bindings)
    child = injector.get(Child)
    
    assert child._fetcher is post_fetcher
    
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
    
def test_can_extend_injectors_with_further_bindings():
    base_bindings = Bindings()
    base_bindings.bind("maximum_threads").to_instance(5)
    base_injector = Injector(base_bindings)
    
    bindings = Bindings()
    bindings.bind("minimum_threads").to_instance(2)
    injector = Injector(bindings, base_injector)

    assert_equals(injector.get("minimum_threads"), 2)
    assert_equals(injector.get("maximum_threads"), 5)
