from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import validate_email
from django.contrib.sites.models import RequestSite

from controller.utils import send_email_template
from registration.backends.default.views import ActivationView, RegistrationView

class RegistrationClosedView(RegistrationView):
    """
    Registration disabled. Only the admins can create new users.
    """
    def registration_allowed(self, request):
        return False

class ActivationRestrictedView(ActivationView):
    """
    The user registration needs be approved by the administrators
    after the account confirmation
    """
    def activate(self, request, activation_key):
        """
        Mark the account as email confirmed and send an email to
        the administrators asking their approval.
        """
        activated = super(ActivationRestrictedView, self).activate(request, activation_key)
        if activated:
            # email confirmed but user still remains disabled
            activated.is_active = False
            activated.save()

            # send mail admin requesting enable the account
            site = RequestSite(request)
            context = { 'request': request, 'site': site, 'user': activated }
            template = 'registration/account_approve_request.email'
            to = settings.EMAIL_REGISTRATION_APPROVE
            # check if is a valid email
            try:
                validate_email(to)
            except ValidationError:
                raise ImproperlyConfigured("EMAIL_REGISTRATION_APPROVE must "\
                    "be a valid email address (current value '%s' is not)." % to)
            send_email_template(template=template, context=context, to=to)

        return activated

