from __future__ import absolute_import

from django.core.exceptions import FieldError
from rest_framework.filters import BaseFilterBackend

from .exceptions import UnprocessableEntity


def value_casting(value):
    """
    Given a str value passed as URL parameter return a
    typed one based on REST API filtering specs.
    
    Can raise UnprocessableEntity
    """
    # string must be put inside double quotes
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1] # strip double quotes
        value = value.replace('""', '"') # remove duplicated quotes
        return value
    # then should be an integer
    try:
        value = int(value)
    except ValueError:
        raise UnprocessableEntity("Filtering using invalid type. Have you "
                                  "forgotten to put string value inside "
                                  "double quotes?")
    return value


def json_pointer_to_django(pointer):
    """
    Translate JSON Pointer to Django queryset syntax.
    http://tools.ietf.org/html/draft-ietf-appsawg-json-pointer-03
    https://docs.djangoproject.com/en/dev/ref/models/querysets/#filter
    
    """
    # remove initial slash (references is always to the object)
    attr = pointer.lstrip('/')
    # django handles nested objects (lists) same way than other attributes
    attr = attr.replace('/_/', '/')
    # translate json pointer syntax to django queryset
    return attr.replace('/', '__')


class ControllerFilterBackend(BaseFilterBackend):
    """
    CONFINE REST API Filtering implementation.
    https://wiki.confine-project.eu/arch:rest-api#filtering
    
    Can raise UnprocessableEntity
    """
    def filter_queryset(self, request, queryset, view):
        """Filter base queryset against query parameters."""
        kwargs = {}
        for attr, value in request.QUERY_PARAMS.iteritems():
            # exclude pagination and member selection parameters of filtering
            # TODO encapsule these parameters as configurable settings
            # or implement a path-like format detector (#584)
            if attr in ['page', 'per_page', 'show']:
                continue
            attr = json_pointer_to_django(attr)
            value = value_casting(value)
            kwargs[attr] = value
        try:
            queryset = queryset.filter(**kwargs)
        except FieldError:
            # Filtering by a non existent field (ignoring)
            raise UnprocessableEntity("Filtering by a non existent field!")
        except ValueError:
            # Filtering using invalid type (e.g. string for an ID)
            raise UnprocessableEntity("Filtering  using invalid type!")
        return queryset
