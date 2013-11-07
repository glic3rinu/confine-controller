from controller.utils import send_email_template

from django.conf import settings
from django.db import models
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from users.models import Group, Roles
try:
    from django.contrib.auth import get_user_model
except ImportError: # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()

class GroupRegistrationManager(models.Manager):
    """
    Custom manager for the ``GroupRegistration`` model.
    
    The methods defined here provide shortcuts for group request 
    creation and its management [aceept|reject] (including emailing).
    
    """
    @transaction.atomic
    def create_group_registration(self, name, desc, username, email, password, user=None):
        """
        Creates a new group registration associating the user who
        request it and a created group storing the provided
        information. If no user has provided, a new inactive
        user is created with the username, email and password

        """
        new_group = Group.objects.create(name=name, description=desc, is_approved=False)

        if user is None: # create new user
            user = User.objects.create_user(username, email, password)
            user.is_active = False
            user.save()

        return self.create(group=new_group, user=user)


class GroupRegistration(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'))
    group = models.ForeignKey(Group, verbose_name=_('group'))
    date = models.DateTimeField('requested date', auto_now=True)
    # NOT necessary: if exists --> not approved, otherwise approved
    #is_approved = models.BooleanField(default=False,
    #    help_text='Designates if a group has been approved by the operations '
    #              'team. When someone sends a request, a group pending of '
    #              'be approved is created.')

    objects = GroupRegistrationManager()

    class Meta:
        verbose_name = 'group registration'
        verbose_name_plural = 'group registrations'

    def __unicode__(self):
        return "%s by %s at %s" % (self.group, self.user, self.date)

    @classmethod
    def is_group_approved(cls, group):
        """ 
        Returns if a group has been approved by operators team. When someone
        sends a request, a group pending of be approved is created.
        """
        return not cls.objects.filter(group=group).exists()

    def approve(self):
        """
        Approving the registration of a group implies the next actions:
        - The associated group will be approved
        - The associated user will be enabled
        - The registration group instance will be removed
        - The group admins will be notified by email
        """
         # create admin role
        Roles.objects.create(user=self.user, group=self.group, is_admin=True)
        
        # enable the user
        self.user.is_active = True
        self.user.save()
        
        # notify the group admin
        self.notify_user(template='registration_group_approved.txt')
        
        # mark the group as approved
        self.delete()

    def reject(self):
        """
        Rejecting the registration of a group implies the next actions:
        - The associated group will be removed
        - The associated user will be removed (except belongs to another group)
        - The registration group instance will be removed
        - The group admins will be notified by email
        """
        # notify the group admin
        self.notify_user(template='registration_group_rejected.txt')

        if not self.user.is_active:
            self.user.delete()

        self.group.delete()
        self.delete()

    def notify_user(self, template):
        context = {'group': self.group, 'user': self.user}
        send_email_template(template=template,
                           context=context,
                           email_from=settings.MAINTEINANCE_EMAIL,
                           to=self.user.email)

    def notify_operators(self):
        #TODO who are the operators?
        template = 'registration_group_creation_mail_operators.txt'
        context = {'group': self.group, 'user': self.user}
        operators_email = settings.MAINTEINANCE_EMAIL
        send_email_template(template=template,
                           context=context,
                           email_from=settings.MAINTEINANCE_EMAIL,
                           to=operators_email)

    def save(self, *args, **kwargs):
        # Only notify when the GroupRegistration was successfully created
        if self.pk:
            self.notify_operators()
            self.notify_user('registration_group_creation_mail_user.txt')
        super(GroupRegistration, self).save(*args, **kwargs)

