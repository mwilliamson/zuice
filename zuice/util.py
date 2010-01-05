class Factory(object):
    def __init__(self, type_):
        self.build = type_

def create_factory(type_):
    return Factory(type_)
