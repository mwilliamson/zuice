from nose.tools import assert_raises

from zuice.django import respond_with_builder
from zuice.django import create_bindings
from zuice.bindings import Bindings
from zuice import NoSuchBindingException
from zuice import inject_by_name
from zuice import Injectable
from zuice import inject

class Url(object):
    def __init__(self, regex, view, kwargs, name):
        self.regex = regex
        self.view = view
        self.kwargs = kwargs
        self.name = name

class Response(object):
    def __init__(self, response):
        self._response = response
        
    def render(self, request):
        return self._response

def test_creates_view_function_that_delegates_to_the_passed_view_class():
    class SimpleView(object):
        def respond(self):
            return Response("simple")
            
    respond_with = respond_with_builder(Bindings())
    view = respond_with(SimpleView)
    assert "simple" == view(None)
    
def test_kwargs_are_passed_to_view():
    class View(object):
        def respond(self, year, month):
            return Response({'year': year, 'month': month})
    
    year = "2000"
    month = "09"
    
    respond_with = respond_with_builder(Bindings())
    view = respond_with(View)
    assert {'year': year, 'month': month} == view(None, year=year, month=month)

def test_binds_request_to_injector_for_response():
    class View(object):
        def respond(self, request):
            return Response(request)
            
    request = {}
    respond_with = respond_with_builder(Bindings())
    view = respond_with(View)
    assert view(request) is request

def test_does_not_bind_request_to_constructor_injector():
    class View(object):
        @inject_by_name
        def __init__(self, request):
            pass
            
        def respond(self):
            return None
            
    request = {}
    respond_with = respond_with_builder(Bindings())
    view = respond_with(View)
    assert_raises(NoSuchBindingException, lambda: view(request))

def test_uses_passed_bindings_in_constructor_and_respond():
    class Request(object):
        method = "POST"
        POST = {"add_to_favs": "true"}
        
    def _request_to_post_parameters(request):
        if request.method == "POST":
            return request.POST
        return None
    
    class View(Injectable):
        _tag_fetcher = inject('tag_fetcher')
    
        def respond(self, post_parameters, year, month):
            return Response({'tag_fetcher': self._tag_fetcher, 'post': post_parameters,
                             'year': year, 'month': month})
    
    tag_fetcher = {}
    bindings = Bindings()
    bindings.bind("tag_fetcher").to_instance(tag_fetcher)
    bindings.bind("post_parameters").to_provider(_request_to_post_parameters)
    respond_with = respond_with_builder(bindings)
    
    year = "2000"
    month = "09"
    
    view = respond_with(View)
    response = view(Request(), year=year, month=month)
    assert response['year'] is year
    assert response['month'] is month
    assert response['tag_fetcher'] is tag_fetcher
    assert response['post'] is Request.POST

class test_passed_bindings_are_not_modified():
    class SimpleView(object):
        def respond(self):
            return Response("simple")
    
    bindings = Bindings()
    respond_with = respond_with_builder(bindings)
    view = respond_with(SimpleView)
    view(None)
    
    assert len(bindings._bindings) == 0

def test_injected_database_saves_objects():
    class Tag(object):
        def __init__(self):
            self.saved = False
        def save(self):
            self.saved = True
    
    class SavingView(object):
        @inject_by_name
        def __init__(self, database):
            self.database = database
            
        def respond(self, tag):
            self.database.save(tag)
            return Response("")

    tag = Tag()
    assert not tag.saved
    
    bindings = create_bindings()
    bindings.bind("tag").to_instance(tag)
    
    respond_with = respond_with_builder(bindings)
    view = respond_with(SavingView)
    response = view(None)
    
    assert tag.saved
    
def test_post_parameters_are_retrieved_from_django_request():
    class Request(object):
        method = "POST"
        POST = {"add_to_favs": "true"}
        
    class View(object):
        def respond(self, post_parameters):
            return Response(post_parameters)
    
    respond_with = respond_with_builder(create_bindings())
    
    view = respond_with(View)
    response = view(Request())
    assert response is Request.POST
    
def test_post_parameters_are_none_if_request_method_is_not_post():
    class Request(object):
        method = "GET"
        POST = {"add_to_favs": "true"}
        
    class View(object):
        def respond(self, post_parameters):
            return Response(post_parameters)
    
    respond_with = respond_with_builder(create_bindings())
    
    view = respond_with(View)
    response = view(Request())
    assert response is None
    
