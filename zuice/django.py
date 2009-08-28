django = __import__("django.conf.urls.defaults", {})

from zuice import Injector

def _view_builder(bindings):
    def view(request, view_class, **kwargs):
        view_injector = Injector(bindings)
        view = view_injector.get_from_type(view_class)

        bindings_for_response = bindings.copy()
        bindings_for_response.bind('request').to_instance(request)
        for item in kwargs.iteritems():
            bindings_for_response.bind_name(item[0]).to_instance(item[1])
        
        response_injector = Injector(bindings_for_response)
        response = response_injector.call(view.respond)
        return response.render(request)
        
    return view

def url_to_class_builder(bindings):
    view = _view_builder(bindings.copy())
    def url_to_class(regex, view_class, kwargs=None, name=None):
        if kwargs is None:
            kwargs = {}
        kwargs['view_class'] = view_class
        return django.conf.urls.defaults.url(regex, view, kwargs, name=name)
        
    return url_to_class
    

