VERSION = (0, 6, 75, 'alpha', 0)


def get_version():
    # Don't litter controller/__init__.py with all the get_version stuff.
    # Only import if it's actually called.
    from django.utils.version import get_version
    return get_version(version=VERSION)

