from rest_framework.exceptions import APIException


class ConcurrencyError(Exception):
    """
    Exception related to building images concurrently (not supported)
    """
    pass


class BaseImageNotAvailable(APIException):
    """
    Raised when there is no available base image for a given node architecture
    """
    status_code = 400
    default_detail = "No base image compatible with the architecture of this node."


class UnexpectedImageFormat(Exception):
    """
    Raised when the image file has not the expected type or format
    """
    pass
