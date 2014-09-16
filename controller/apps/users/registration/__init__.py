from __future__ import absolute_import

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from registration.backends.default.views import ActivationView

from .utils import get_backend
from .views import ActivationRestrictedView, RegistrationOpenView, RegistrationClosedView


class BackendFactory(object):
    """
    Factory backend creator
    """
    @classmethod
    def create(cls):
        modes = {
            'OPEN': 'users.registration.OpenBackend',
            'RESTRICTED': 'users.registration.RestrictedBackend',
            'CLOSED': 'users.registration.ClosedBackend' }
        try:
            mode = settings.USERS_REGISTRATION_MODE
            backend = modes.get(mode)
            return get_backend(backend)
        except KeyError:
            raise ImproperlyConfigured('"%s" is not a valid mode for USERS_REGISTRATION_MODE'
                ' Available modes are %s' % (mode, ','.join(modes.keys())))


class OpenBackend(object):
    """
    Wrapper of the django-registration default backend
    1. User submits registration info.
    2. System sends an email to the users with validation link
    3. Once the user has visited the link its account is enabled
    """
    def get_activation_view(self):
        return ActivationView 
    
    def get_registration_view(self):
        return RegistrationOpenView


class RestrictedBackend(OpenBackend):
    """
    The user registration needs be approved by the administrators
    after the account confirmation
    """
    def get_activation_view(self):
        return ActivationRestrictedView 


class ClosedBackend(OpenBackend):
    """
    Registration disabled. Only the admins can create new users.
    """
    def get_registration_view(self):
        return RegistrationClosedView
