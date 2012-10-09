class Register(object):
    def __init__(self):
        self._base_registry = {}
    
    def register(self, name, root_url):
        self._base_registry.update({name: root_url})

    def get_base(self):
        return self._base_registry


api = Register()
