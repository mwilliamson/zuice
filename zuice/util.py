def factory(type_):
    return type("%sFactory" % type_.__name__, (object, ), {"build": type_})
