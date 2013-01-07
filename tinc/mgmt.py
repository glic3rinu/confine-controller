class TincBackend(object):
    """ 
    Management Backend class that provides the managemnt address to the testbed
    components.
    """
    def address(self, obj):
        """ Relies on obj.tinc.address wich is provided by this same app """
        return obj.tinc.address


backend = TincBackend()
