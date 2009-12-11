django = __import__("django.template", {})
template = django.template

from functools import wraps

from zuice import Injector
from zuice.bindings import Bindings

def respond_with_builder(bindings):
    view_injector = Injector(bindings)
    
    def respond_with(view_class):
        def view(request, **kwargs):
            view = view_injector.get_from_type(view_class)

            bindings_for_response = bindings.copy()
            bindings_for_response.bind('request').to_instance(request)
            for item in kwargs.iteritems():
                bindings_for_response.bind(item[0]).to_instance(item[1])
            
            response_injector = Injector(bindings_for_response)
            response = response_injector.call(view.respond)
            return response.render(request)
            
        return view
        
    return respond_with

class Database(object):
    def save(self, to_save):
        to_save.save()
            
def _request_to_post_parameters(request):
    if request.method == "POST":
        return request.POST
    return None
    
def create_bindings():
    bindings = Bindings()
    bindings.bind('database').to_type(Database)
    bindings.bind("post_parameters").to_provider(_request_to_post_parameters)
    bindings.bind("user").to_provider(lambda request: request.user)
    return bindings

class InjectedNode(template.Node):
    def __init__(self, base_node, bindings_variable):
        self._base_node = base_node
        self._bindings_variable = bindings_variable
        
    def render(self, context):
        bindings = self._bindings_variable.resolve(context).copy()
        bindings.bind("context").to_instance(context)
        injector = Injector(bindings)
        return injector.call(self._base_node.render)

def injectable_tag(function):
    @wraps(function)
    def tag_function(*args, **kwargs):
        return InjectedNode(function(*args, **kwargs), template.Variable("bindings"))
        
    return tag_function
