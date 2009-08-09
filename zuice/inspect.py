inspect = __import__('inspect', {})

class Argument(object):
    def __init__(self, name, has_default, default):
        self.name = name
        self.has_default = has_default
        self.default = default
        
def get_method_args_spec(function):
    return _get_args_spec(function, True)

def get_function_args_spec(function):
    return _get_args_spec(function, False)
    
def _get_args_spec(function, remove_first_arg):
    arg_specs = inspect.getargspec(function)
    arg_names = arg_specs[0]
    if remove_first_arg:
        arg_names = arg_names[1:]
    default_args = arg_specs[3] or []
    number_of_required_args = len(arg_names) - len(default_args)
    has_defaults = ([False] * number_of_required_args) + ([True] * len(default_args))
    defaults = ([None] * number_of_required_args) + list(default_args)
    
    return map(lambda i: Argument(arg_names[i], has_defaults[i], defaults[i]), range(0, len(arg_names)))
    
