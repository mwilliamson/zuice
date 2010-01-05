class Factory(object):
    def __init__(self, type_):
        self.build = type_

def factory(type_):
    return Factory(type_)
