class OperationLocked(Exception):
    """
    Raised when an operation can not be executed because of a lock
    """
    pass


class InvalidMgmtAddress(Exception):
    """ 
    Raised when the mgmt address is invalid or object does not exists
    """
    pass
