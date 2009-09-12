from functools import wraps

import zuice.reflect

def auto_assign(constructor):
    arg_specs = zuice.reflect.get_args_spec(constructor)
    arg_names = [arg.name for arg in arg_specs]
    @wraps(constructor)
    def new_constructor(self, *args, **kwargs):
        for index in range(0, len(args)):
            setattr(self, arg_specs[index].name, args[index])
            
        for index in range(len(args), len(arg_specs)):
            arg_spec = arg_specs[index]
            arg_name = arg_spec.name
            if arg_name in kwargs:
                setattr(self, arg_name, kwargs[arg_name])
            elif arg_spec.has_default:
                setattr(self, arg_name, arg_spec.default)
        
        for key in kwargs:
            if key not in arg_names:
                setattr(self, key, kwargs[key])
        
        constructor(self, *args, **kwargs)
    return new_constructor
