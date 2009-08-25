from zuice.decorators import auto_assign

def test_positional_arguments_are_assigned_to_fields():
    class Foo(object):
        @auto_assign
        def __init__(self, x, y):
            pass
            
    foo = Foo(4, "pourquoi")
    assert foo.x == 4
    assert foo.y == "pourquoi"

def test_keyword_arguments_are_assigned_to_fields():
    class Foo(object):
        @auto_assign
        def __init__(self, x, y):
            pass
            
    foo = Foo(4, y="pourquoi")
    assert foo.x == 4
    assert foo.y == "pourquoi"

def test_defaults_are_assigned_to_fields():
    class Foo(object):
        @auto_assign
        def __init__(self, x, y="pourquoi"):
            pass
            
    foo = Foo(4)
    assert foo.x == 4
    assert foo.y == "pourquoi"

def test_original_constructor_is_called_after_assignment():
    class Foo(object):
        @auto_assign
        def __init__(self, x, y):
            self.x = self.x + 10
            
    foo = Foo(4, "pourquoi")
    assert foo.x == 14
    assert foo.y == "pourquoi"

def test_constructors_are_wrapped():
    class Foo(object):
        @auto_assign
        def __init__(self, x):
            """Docstring"""
            pass
    assert Foo.__init__.__name__ == '__init__'
    assert Foo.__init__.__doc__ == 'Docstring'
