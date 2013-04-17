class VlanAllocationError(Exception):
    """ 
    There is a problem allicating vlan numbers
    """
    pass


class IfaceAllocationError(Exception):
    """ 
    Raised when there is not possible to allocat a requested iface
    """
    pass
