from functools import wraps

import zuice.inspect

def auto_assign(constructor):
    arg_specs = zuice.inspect.get_args_spec(constructor)
    @wraps(constructor)
    def new_constructor(self, *args, **kwargs):
        for index in range(0, len(args)):
            setattr(self, arg_specs[index].name, args[index])
        for index in range(len(args), len(arg_specs)):
            arg_name = arg_specs[index].name
            setattr(self, arg_name, kwargs[arg_name])
        constructor(self, *args, **kwargs)
    return new_constructor
