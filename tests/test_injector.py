from nose.tools import assert_equal
from nose.tools import assert_raises

import zuice
from zuice import Bindings
from zuice import Injector
from zuice import NoSuchBindingException
from zuice import dependency
from zuice import Base

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
    assert injector.get(Apple) is apple

def test_bind_name_to_instance():
    apple = Apple()
    bindings = Bindings()
    bindings.bind("apple").to_instance(apple)
    
    injector = Injector(bindings)
    assert injector.get("apple") is apple
    
def test_bind_type_to_provider():
    apple = Apple()
    bindings = Bindings()
    bindings.bind(Apple).to_provider(lambda injector: apple)
    
    injector = Injector(bindings)
    assert injector.get(Apple) is apple


def test_get_throws_exception_if_no_such_binding_exists_and_object_has_init_args():
    class Donkey(object):
        def __init__(self, legs):
            pass
        
    injector = Injector(Bindings())
    assert_raises(NoSuchBindingException, lambda: injector.get(Donkey))
    
def test_get_raises_exception_if_no_such_binding_exists():
    injector = Injector(Bindings())
    assert_raises(NoSuchBindingException, lambda: injector.get("apple"))
    
    apple = Apple()
    bindings = Bindings()
    bindings.bind("apple").to_provider(lambda injector: apple)
    
    injector = Injector(bindings)
    assert injector.get("apple") is apple
    assert_raises(NoSuchBindingException, lambda: injector.get("banana"))

def test_changing_bindings_after_creating_injector_does_not_change_injector():
    bindings = Bindings()
    injector = Injector(bindings)
    bindings.bind("apple").to_instance(Apple())
    assert_raises(NoSuchBindingException, lambda: injector.get("apple"))


def test_can_inject_class_with_no_constructor_arguments():
    class Coconut(object):
        def __init__(self):
            self.x = 10
            
    injector = Injector(Bindings())
    coconut = injector.get(Coconut)
    assert_equal(10, coconut.x)


def test_can_bind_to_names():
    apple_to_inject = Apple()
    bindings = Bindings()
    bindings.bind("apple").to_instance(apple_to_inject)
    bindings.bind("another_apple").to_key("apple")
    
    injector = Injector(bindings)
    assert injector.get("another_apple") is apple_to_inject


def test_injector_class_is_bound_to_injector():
    injector = Injector(Bindings())
    assert injector.get(Injector) is injector
    

def test_classes_that_inherit_from_injectable_have_members_injected():
    class Foo(Base):
        _tag_fetcher = dependency("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    
    bindings = Bindings()
    bindings.bind("tag_fetcher").to_instance(tag_fetcher)
    injector = Injector(bindings)
    assert injector.get(Foo)._tag_fetcher is tag_fetcher

def test_classes_that_inherit_from_injectable_can_be_passed_constructor_arguments_manually_by_name():
    class Foo(Base):
        fetcher = dependency("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    
    assert Foo(fetcher=tag_fetcher).fetcher is tag_fetcher

def test_injectable_members_have_leading_underscores_removed_in_constructor_arg():
    class Foo(Base):
        _fetcher = dependency("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    
    assert Foo(fetcher=tag_fetcher)._fetcher is tag_fetcher

def test_classes_that_inherit_from_injectable_can_be_passed_constructor_arguments_manually_by_position():
    class View(Base):
        _tag_fetcher = dependency("tag_fetcher")
        _post_fetcher = dependency("post_fetcher")
    
    tag_fetcher = {'some': 'object'}
    post_fetcher = {'another': 'object'}
    
    view = View(tag_fetcher, post_fetcher)
    assert view._tag_fetcher is tag_fetcher
    assert view._post_fetcher is post_fetcher

def test_injecting_overspecified_arguments_to_injectable_raises_exception():
    class View(Base):
        _tag_fetcher = dependency("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    
    try:
        view = View(tag_fetcher, tag_fetcher=tag_fetcher)
        assert False
    except TypeError as e:
        assert_equal(str(e), "Got multiple values for keyword argument 'tag_fetcher'")

def test_injecting_too_many_positional_arguments_to_injectable_raises_exception():
    class View(Base):
        _tag_fetcher = dependency("tag_fetcher")
    
    try:
        view = View(None, None)
        assert False
    except TypeError as e:
        assert_equal(str(e), "__init__ takes exactly 2 arguments (3 given)")

def test_injectable_injects_attributes_of_sub_classes():
    class Parent(Base):
        _tag_fetcher = dependency('tag_fetcher')
        
    class Child(Parent):
        _blog_post_fetcher = dependency('post_fetcher')

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
    class Parent(Base):
        _fetcher = dependency('tag_fetcher')
        
    class Child(Parent):
        _fetcher = dependency('post_fetcher')

    post_fetcher = {'another': 'object'}
    
    bindings = Bindings()
    bindings.bind("post_fetcher").to_instance(post_fetcher)
    injector = Injector(bindings)
    child = injector.get(Child)
    
    assert child._fetcher is post_fetcher
    
def test_missing_constructor_arguments_in_injectable_raises_type_error():
    class Foo(Base):
        _tag_fetcher = dependency("tag_fetcher")
        _blog_post_fetcher = dependency('post_fetcher')
    
    tag_fetcher = {'some': 'object'}
    
    assert_raises(TypeError, lambda: Foo(_tag_fetcher=tag_fetcher))

def test_injectable_injecting_manually_with_extra_members_raises_type_error():
    class Foo(Base):
        _tag_fetcher = dependency("tag_fetcher")
    
    tag_fetcher = {'some': 'object'}
    post_fetcher = {'another': 'object'}
    
    assert_raises(TypeError, lambda: Foo(_tag_fetcher=tag_fetcher, _post_fetcher=post_fetcher))
    

def test_can_set_bindings_for_keys_in_call_to_get():
    Name = zuice.key("Name")
    injector = Injector(Bindings())
    assert_equal("Bob", injector.get(Name, {Name: "Bob"}))
    

def test_unscoped_injectables_are_available_in_any_scope():
    Greeting = zuice.key("Greeting")
    Name = zuice.key("Name")
    
    class Greeter(zuice.Base):
        _greeting = zuice.dependency(Greeting)
        _name = zuice.dependency(Name)
        
        def hello(self):
            return "{0} {1}".format(self._greeting, self._name)
    
    bindings = Bindings()
    bindings.bind(Greeting).to_instance("Hello")
    injector = Injector(bindings)
    greeter = injector.get(Greeter, {Name: "Bob"})
    assert greeter.hello() == "Hello Bob"
    

def test_scoped_injectables_cannot_depend_on_injectables_in_separate_scope():
    Name = zuice.key("Name")
    
    class Greeter(zuice.Base):
        _name = zuice.dependency(Name)
    
    bindings = Bindings()
    bindings.bind(Greeter).singleton()
    injector = Injector(bindings)
    error = assert_raises(NoSuchBindingException, lambda: injector.get(Greeter, {Name: "Bob"}))
    # TODO
    #~ assert_equal(Name, error.key)
    

def test_can_set_bindings_for_keys_in_call_to_injected_factory():
    Name = zuice.key("Name")
    
    class Greeter(zuice.Base):
        _name = zuice.dependency(Name)
        
        def hello(self):
            return "Hello {0}".format(self._name)
    
    injector = Injector(Bindings())
    factory = injector.get(zuice.factory(Greeter))
    greeter = factory({Name: "Bob"})
    assert greeter.hello() == "Hello Bob"
    

def test_original_bindings_are_prefered_to_zero_arg_constructors():
    class Unit(object):
        pass
    
    unit = Unit()
    
    bindings = Bindings()
    bindings.bind(Unit).to_instance(unit)
    
    injector = Injector(bindings)
    assert injector.get(Unit, {zuice.key("a"): "a"}) is unit


class TestLifetimes(object):
    def test_new_instances_are_returned_by_default(self):
        x = [0]
        class Counter(object):
            def __init__(self):
               self.x = x[0] = x[0] + 1 
        
        bindings = Bindings()
        injector = Injector(bindings)
        
        assert_equal(1, injector.get(Counter).x)
        assert_equal(2, injector.get(Counter).x)
    
    def test_bindings_can_change_lifetime_to_singleton(self):
        x = [0]
        class Counter(object):
            def __init__(self):
               self.x = x[0] = x[0] + 1
        
        bindings = Bindings()
        bindings.bind(Counter).singleton()
        injector = Injector(bindings)
        
        assert_equal(1, injector.get(Counter).x)
        assert_equal(1, injector.get(Counter).x)
    
    def test_bindings_can_change_lifetime_of_provider_to_singleton(self):
        x = [0]
        
        def count(injector):
            x[0] += 1
            return x[0]
        
        counter = zuice.key("counter")
        bindings = Bindings()
        bindings.bind(counter).to_provider(count).singleton()
        injector = Injector(bindings)
        assert_equal(1, injector.get(counter))
        assert_equal(1, injector.get(counter))
    
    def test_bindings_can_scope_provider_to_value(self):
        x = []
        
        Name = zuice.key("Name")
        
        def count(injector):
            name = injector.get(Name)
            x.append(name)
            return x
        
        counter = zuice.key("counter")
        bindings = Bindings()
        
        with bindings.scope(Name) as scope_bindings:
            scope_bindings.bind(counter).to_provider(count)
        
        injector = Injector(bindings)
        assert_equal(["Bob"], injector.get(counter, {Name: "Bob"}))
        assert_equal(["Bob"], injector.get(counter, {Name: "Bob"}))
        assert_equal(["Bob", "Jim"], injector.get(counter, {Name: "Jim"}))
    
    def test_can_retrieve_scoped_value_when_scoped_value_is_set_alongside_other_values(self):
        x = []
        
        Name = zuice.key("Name")
        Greeting = zuice.key("Greeting")
        
        def count(injector):
            name = injector.get(Name)
            x.append(name)
            return x
        
        counter = zuice.key("counter")
        bindings = Bindings()
        
        with bindings.scope(Name) as scope_bindings:
            scope_bindings.bind(counter).to_provider(count)
        
        injector = Injector(bindings)
        assert_equal(["Bob"], injector.get(counter, {Name: "Bob", Greeting: "hello"}))
    
    
    def test_singleton_is_cached_in_singleton_scope_when_injector_is_not_in_singleton_scope(self):
        x = [0]
        class Counter(object):
            def __init__(self):
               self.x = x[0] = x[0] + 1
        
        bindings = Bindings()
        bindings.bind(Counter).singleton()
        injector = Injector(bindings)
        
        assert_equal(1, injector.get(Counter, {"name": "Bob"}).x)
        assert_equal(1, injector.get(Counter).x)
    
    
    def test_cached_singleton_is_available_from_non_singleton_scope(self):
        x = [0]
        class Counter(object):
            def __init__(self):
               self.x = x[0] = x[0] + 1
        
        bindings = Bindings()
        bindings.bind(Counter).singleton()
        injector = Injector(bindings)
        
        assert_equal(1, injector.get(Counter, {"name": "Bob"}).x)
        assert_equal(1, injector.get(Counter, {"name": "Jim"}).x)

    
def test_methods_decorated_with_init_decorator_are_run_after_injection():
    class Count(zuice.Base):
        @zuice.init
        def start(self):
            self.x = 1
    
    injector = Injector(Bindings())
    assert_equal(1, injector.get(Count).x)

    
def test_methods_decorated_with_init_decorator_are_run_after_manual_construction():
    class Count(zuice.Base):
        @zuice.init
        def start(self):
            self.x = 1
    
    assert_equal(1, Count().x)
