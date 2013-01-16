class TincBackend(object):
    """ 
    Management Backend class that provides the managemnt address to some testbed components
    """
    name = 'tinc'
    
    def address(self, obj):
        """ Relies on obj.tinc.address wich is provided by this same app """
        return obj.tinc.address


backend = TincBackend()
