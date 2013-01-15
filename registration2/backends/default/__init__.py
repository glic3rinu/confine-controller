from django.db import transaction
from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from registration2.forms import GroupRegistrationForm
from registration2.models import GroupRegistration

try:
    from django.contrib.auth import get_user_model
except ImportError: # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()


class UserGroup(object): #TODO is subclassing register backend needed??
    @transaction.commit_on_success
    def group_register(self, request, **kwargs):
        """
        Create a new group registration.
        1. Register an unapproved group in the system
        2. Register an inactive user
        3. Send an email to the operators requesting group approval

        """
        name, desc = kwargs['name'], kwargs['description']
        username, email, password = kwargs['user-username'], kwargs['user-email'], kwargs['user-password1']
        
        new_group_reg = GroupRegistration.objects.create_group_registration(name, desc, username, email, password)
        
        return new_group_reg

    def group_get_form_class(self, request):
        return GroupRegistrationForm

    def group_post_registration_redirect(self, request, group_registration):
        return ('registration_group_complete', (), {})
