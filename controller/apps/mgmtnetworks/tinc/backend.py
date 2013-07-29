class TincBackend(object):
    """
    Management Backend class that provides the managemnt address to some testbed components
    """
    def __init__(self, obj):
        self.obj = obj
    
    @property
    def name(self):
        return self.obj.tinc._meta.verbose_name.replace(' ', '_')
    
    @property
    def addr(self):
        return self.obj.tinc.address
    
    def tinc_client(self):
        return self.obj.tinc if self.name == 'tinc_client' else None
    
    def tinc_server(self):
        return self.obj.tinc if self.name == 'tinc_server' else None
    
    def is_configured(self):
        return bool(self.obj.tinc.pubkey)
    
    @property
    def native(self):
        return None
