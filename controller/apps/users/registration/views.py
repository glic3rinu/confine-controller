from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import validate_email
from django.contrib.sites.models import RequestSite, Site

from registration import signals
from registration.backends.default.views import ActivationView, RegistrationView

from controller.utils import send_email_template
from .models import RegistrationProfile


class RegistrationOpenView(RegistrationView):
    """
    Regitration open, everyone can register as user.
    
    """
    def register(self, request, **cleaned_data):
        """ Initialize custom user data model """
        username, name, email, password = (cleaned_data['username'],
            cleaned_data['name'], cleaned_data['email'], cleaned_data['password1'])
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        
        new_user = RegistrationProfile.extra_manager.create_inactive_user(
                        username, name, email, password, site)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user


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
        activated_user = RegistrationProfile.extra_manager.activate_user(activation_key, enable=False)
        
        if activated_user:
            # email confirmed but user still remains disabled
            # send mail admin requesting enable the account
            site = RequestSite(request)
            context = { 'request': request, 'site': site, 'user': activated_user }
            template = 'registration/account_approve_request.email'
            to = settings.EMAIL_REGISTRATION_APPROVE
            # check if is a valid email
            try:
                validate_email(to)
            except ValidationError:
                raise ImproperlyConfigured("EMAIL_REGISTRATION_APPROVE must "\
                    "be a valid email address (current value '%s' is not)." % to)
            send_email_template(template=template, context=context, to=to)

        return activated_user

