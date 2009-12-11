from datetime import datetime

from django import template

from nose.tools import assert_raises
from nose.tools import assert_equals
from funk import with_context
from funk import expects
from funk import allows
from funk import expects_call
from funk.matchers import Matcher

from zuice.django import respond_with_builder
from zuice.django import create_bindings
from zuice.django import injectable_tag
from zuice.django import register_injectable_simple_tag
from zuice.bindings import Bindings
from zuice import Injector
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
    
def test_user_is_bound():
    user = {}
    
    class Request(object):
        def __init__(self):
            self.user = user
        
    class View(object):
        def respond(self, user):
            return Response(user)
    
    respond_with = respond_with_builder(create_bindings())
    
    view = respond_with(View)
    response = view(Request())
    assert response is user

@with_context    
def test_injectable_tags_use_injector_from_template_context(context):
    class FormattedDateNode(template.Node):
        def __init__(self, date_variable_name):
            self.date_variable_name = date_variable_name
            
        def render(self, context, date_formatter):
            date = template.Variable(self.date_variable_name).resolve(context)
            return date_formatter.format(date)
    
    @injectable_tag
    def format_date(parser, token):
        tag_name, date_variable_name = token.split_contents()
        return FormattedDateNode(date_variable_name)
        
    date_formatter = context.mock()
    token = context.mock()
    date = datetime(2009, 12, 11)
    date_variable_name = "date"
    formatted_string = "11th December 2009"
    
    bindings = Bindings()
    bindings.bind("date_formatter").to_instance(date_formatter)
    template_context = {"injector": Injector(bindings), date_variable_name: date}
    
    expects(token).split_contents().returns(["format_date", date_variable_name])
    expects(date_formatter).format(date).returns(formatted_string)
    
    node = format_date(None, token)
    assert_equals(node.render(template_context), formatted_string)

def test_injectable_tags_retain_their_name():
    @injectable_tag
    def format_date(parser, token):
        pass
        
    assert_equals("format_date", format_date.__name__)

@with_context
def test_injectable_simple_tags_use_injector_from_template_context(context):
    class IsInjectedFormatDateTag(Matcher):
        def matches(self, value, mismatch_output):
            token = context.mock()
            date_formatter = context.mock()
            
            date = datetime(2009, 12, 11)
            date_variable_name = "date"
            formatted_string = "11th December 2009"
            
            bindings = Bindings()
            bindings.bind("date_formatter").to_instance(date_formatter)
            template_context = {"injector": Injector(bindings), date_variable_name: date}
            
            expects(date_formatter).format(date).returns(formatted_string)
            expects(token).split_contents().returns(["format_date", date_variable_name])
            
            return value(None, token).render(template_context) == formatted_string
            
        def __str__(self):
            return "<injected version of format date tag>"
    
    class FormatDateTag(Injectable):
        _date_formatter = inject("date_formatter")
        
        def render(self, date):
            return self._date_formatter.format(date)
    
    library = context.mock()
    tag_register = context.mock()
    
    expects(library).tag("format_date").returns(tag_register)
    expects_call(tag_register).with_args(IsInjectedFormatDateTag())
    
    register_injectable_simple_tag(library, "format_date", FormatDateTag)
