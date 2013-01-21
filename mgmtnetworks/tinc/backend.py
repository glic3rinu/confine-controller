class TincBackend(object):
    """ 
    Management Backend class that provides the managemnt address to some testbed components
    """
    def address(self, obj):
        """ Relies on obj.tinc.address wich is provided by this same app """
        return obj.tinc.address
    
    @property
    def name(self, obj):
        return obj.tinc._meta.verbose_name.replace(' ', '_')

backend = TincBackend()
