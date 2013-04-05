from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.core.exceptions import ImproperlyConfigured

from controller.utils import send_email_template

from registration.backends.default import DefaultBackend

class BackendFactory(object):
    """
    Factory backend creator
    """
    @classmethod
    def create(cls):
        mode = settings.USERS_REGISTRATION_MODE
        if mode == 'OPEN':
            return 'users.backends.registration.OpenBackend' #OpenBackend()
        elif mode == 'RESTRICTED':
            return 'users.backends.registration.RestrictedBackend' #RestrictedBackend()
        elif mode == 'CLOSED':
            return 'users.backends.registration.ClosedBackend' #ClosedBackend()
        else:
            raise ImproperlyConfigured('USERS_REGISTRATION_MODE value is "%s" '
                'but valid options are "OPEN", "RESTRICTED" or "CLOSED".' % mode)

    
class OpenBackend(DefaultBackend):
    """
    Wrapper of the django-registration default backend
    1. User submits registration info.
    2. System sends an email to the users with validation link
    3. Once the user has visited the link its account is enabled
    """
    pass

class RestrictedBackend(DefaultBackend):
    """
    The user registration needs be approved by the administrators
    after the account confirmation
    """
    def activate(self, request, activation_key):
        """
        Mark the account as email confirmed and send an email to
        the administrators asking their approval.
        """
        activated = super(RestrictedBackend, self).activate(request, activation_key)
        if activated:
            # email confirmed but user still remains disabled
            activated.is_active = False
            activated.save()

            # send mail admin requesting enable the account
            site = RequestSite(request)
            context = { 'request': request, 'site': site, 'user': activated }
            template = 'registration/account_approve_request.email'
            to = settings.EMAIL_REGISTRATION_APPROVE
            send_email_template(template=template, context=context, to=to)

        return activated

class ClosedBackend(DefaultBackend):
    """
    Registration disabled. Only the admins can create new users.
    """
    def registration_allowed(self, request):
        return False
