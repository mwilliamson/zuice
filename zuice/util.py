class Factory(object):
    def __init__(self, type_):
        self._type = type_
        
    def build(self, *args, **kwargs):
        return self._type(*args, **kwargs)

def factory(type_):
    return Factory(type_)
