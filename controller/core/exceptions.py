from django.core.exceptions import SuspiciousOperation


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


class DisallowedSliverCreation(SuspiciousOperation):
    """
    Raised when a user tries to access add_sliver URL using a combination
    of slice and node that already have a sliver.
    """
    pass
