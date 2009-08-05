from zuice.original_django import url

from zuice import Injector

def controller_view_builder(bindings):
    def controller_view(request, controller_class, **kwargs):
        controller_injector = Injector(bindings)
        controller = controller_injector.get_from_type(controller_class)

        bindings_for_response = bindings.copy()
        for item in kwargs.iteritems():
            bindings_for_response.bind_name(item[0]).to_instance(item[1])
        
        response_injector = Injector(bindings_for_response)
        response = response_injector.call(controller.respond)
        return response.render(request)
        
    return controller_view

def url_controller_builder(bindings):
    def url_controller(regex, controller_class, kwargs=None, name=None):
        if kwargs is None:
            kwargs = {}
        kwargs['controller_class'] = controller_class
        return url(regex, controller_view_builder(bindings), kwargs, name=name)
        
    return url_controller
    

