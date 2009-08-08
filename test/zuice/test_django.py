from nose.tools import assert_raises

import zuice.django
from zuice.django import url_controller_builder
from zuice.bindings import Bindings
from zuice import NoSuchBindingException
from zuice import inject_by_name

class Url(object):
    def __init__(self, regex, view, kwargs, name):
        self.regex = regex
        self.view = view
        self.kwargs = kwargs
        self.name = name

zuice.django.url = lambda regex, view, kwargs, name: Url(regex, view, kwargs, name)

class Response(object):
    def __init__(self, response):
        self._response = response
        
    def render(self, request):
        return self._response

class SimpleController(object):
    def respond(self):
        return Response("simple")

def test_creates_url_function_that_uses_a_view_that_uses_the_passed_controller():
    url_controller = url_controller_builder(Bindings())
    url = url_controller("regex", SimpleController)
    assert url.regex == "regex"
    assert url.kwargs == {'controller_class': SimpleController}
    assert "simple" == url.view(request=None, **url.kwargs)
    assert url.name is None
    
def test_uses_passed_kwargs_when_creating_url():
    url_controller = url_controller_builder(Bindings())
    url = url_controller("regex", SimpleController, {"foo": 1, "bar": 2})
    assert url.kwargs == {'controller_class': SimpleController, "foo": 1, "bar": 2}

def test_uses_name_if_provided():
    url_controller = url_controller_builder(Bindings())
    url = url_controller("regex", SimpleController, name="NAME")
    assert url.regex == "regex"
    assert url.kwargs == {'controller_class': SimpleController}
    assert "simple" == url.view(request=None, **url.kwargs)
    assert url.name == "NAME"

class RequestBindingController(object):
    @inject_by_name
    def respond(self, request):
        self.request = request
        return Response(request)

def test_binds_request_to_injector_for_response():
    request = {}
    url_controller = url_controller_builder(Bindings())
    url = url_controller("regex", RequestBindingController)
    assert url.view(request, **url.kwargs) is request

class RequestInInitController(object):
    @inject_by_name
    def __init__(self, request):
        pass
        
    def respond(self):
        return None

def test_does_not_bind_request_to_constructor_injector():
    request = {}
    url_controller = url_controller_builder(Bindings())
    url = url_controller("regex", RequestInInitController)
    assert_raises(NoSuchBindingException, lambda: url.view(request, **url.kwargs))
    
class InterestingController(object):
    @inject_by_name
    def respond(self, foo, bar):
        return Response((foo, bar))
    
def test_binds_view_kwargs_to_their_respective_names():
    url_controller = url_controller_builder(Bindings())
    url = url_controller("regex", InterestingController)
    response = url.view(None, foo=1, bar=2, **url.kwargs)
    assert response == (1, 2)

class VeryInterestingController(object):
    @inject_by_name
    def __init__(self, apple):
        self._apple = apple
        
    @inject_by_name
    def respond(self, foo, banana, bar):
        return Response((self._apple, banana, foo, bar))

class Apple(object):
    pass
    
class Banana(object):
    pass

def test_uses_passed_bindings_in_constructor_and_respond():
    apple = Apple()
    banana = Banana()
    bindings = Bindings()
    bindings.bind("apple").to_instance(apple)
    bindings.bind("banana").to_instance(banana)
    url_controller = url_controller_builder(bindings)
    url = url_controller("regex", VeryInterestingController)
    response = url.view(None, foo=1, bar=2, **url.kwargs)
    assert response == (apple, banana, 1, 2)
