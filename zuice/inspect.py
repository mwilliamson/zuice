from zuice.original_inspect import original_inspect as inspect

class Argument(object):
    def __init__(self, name, has_default, default):
        self.name = name
        self.has_default = has_default
        self.default = default
        
def get_method_args_spec(function):
    arg_specs = inspect.getargspec(function)
    arg_names = arg_specs[0][1:]
    default_args = arg_specs[3]
    number_of_required_args = len(arg_names) - len(default_args)
    has_defaults = ([False] * number_of_required_args) + ([True] * len(default_args))
    defaults = ([None] * number_of_required_args) + list(default_args)
    
    return map(lambda i: Argument(arg_names[i], has_defaults[i], defaults[i]), range(0, len(arg_names)))

