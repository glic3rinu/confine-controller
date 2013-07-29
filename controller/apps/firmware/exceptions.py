class ConcurrencyError(Exception):
    """
    Exception related to building images concurrently (not supported)
    """
    pass


class BaseImageNotAvailable(Exception):
    """
    Raised when there is no available base image for a given node architecture
    """
    pass


class UnexpectedImageFormat(Exception):
    """
    Raised when the image file has not the expected type or format
    """
    pass
