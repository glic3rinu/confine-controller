class Register(object):
    def __init__(self):
        self._base_registry = {}

    @property
    def urls(self):
        return self.get_urls()
        
    def get_urls(self):
        for resource in self.resources:
            
    
    def register(self, name, root_url):
        self._base_registry.update({name: root_url})

    def get_base(self):
        return self._base_registry


api = Register()
