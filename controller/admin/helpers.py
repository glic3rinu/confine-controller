class FuncAttrWrapper():
    """ wrapper class for access function attributes on django templates """
    def __init__(self, actions):
        for attr in dir(actions):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(actions, attr))
