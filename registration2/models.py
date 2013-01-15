import datetime
import hashlib
import random
import re

from django.conf import settings
from users.models import User, Group, Roles #TODO import User using custom auth.User
from django.db import models
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now

class GroupRegistrationManager(models.Manager):
    """
    Custom manager for the ``GroupRegistration`` model.
    
    The methods defined here provide shortcuts for group request 
    creation and its management [aceept|reject] (including emailing).
    
    """

    def create_group_registration(self, name, desc, username, email, password):
        # create new group
        new_group = Group.objects.create(name=name, description=desc, is_approved=False)

        #create new user
        new_user = User.objects.create_user(username, email, password)
        
        return self.create(group=new_group, user=new_user)
        
        


class GroupRegistration(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'))
    group = models.ForeignKey(Group, verbose_name=_('group'))
    date = models.DateTimeField('requested date', auto_now=True)

    objects = GroupRegistrationManager()

    def approve(self):
         # create admin role
        Roles.objects.create(user=self.user, group=self.group, is_admin=True)
        
        # mark the group as approved
        self.group.is_approved = True
        self.group.save()
        
        #TODO send mail to inform admin(s)
        #notify the admin
        for email in self.group.get_admin_emails():
            pass #TODO send mail...
            #send_mail(subject, message, from_email, email)
        
        self.delete()

    def reject(self):
        """
        #TODO remove:
        #       + group
        #       + groupRegistration
        #       + user (if not associed to another group == inactive)
        """
        
        #TODO send mail to inform admins
        for email in self.group.get_admin_emails():
            pass #TODO send mail...
        # TODO delete user if is inactive an not belongs to other groups??

        
