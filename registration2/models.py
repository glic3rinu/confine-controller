from common.utils import send_mail_template

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
    @transaction.commit_on_success
    def create_group_registration(self, name, desc, username, email, password):
        # create new group
        new_group = Group.objects.create(name=name, description=desc, is_approved=False)

        # create new user
        new_user = User.objects.create_user(username, email, password)

        return self.create(group=new_group, user=new_user)


class GroupRegistration(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'))
    group = models.ForeignKey(Group, verbose_name=_('group'))
    date = models.DateTimeField('requested date', auto_now=True)

    objects = GroupRegistrationManager()

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
        
        # mark the group as approved
        self.group.is_approved = True
        self.group.save()

        # enable the user
        self.user.is_active = True
        self.user.save()
        
        # notify the group admin
        self.notify_user(template='registration_group_approved.txt')
        
        self.delete()
        #TODO mark redirect to change_list instead GroupReg change_view

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
        #TODO mark redirect to change_list instead GroupReg change_view

    def notify_user(self, template):
        context = {'group': self.group, 'user': self.user}
        send_mail_template(template=template,
                           context=context,
                           email_from=settings.MAINTEINANCE_EMAIL,
                           to=self.user.email)

    def notify_operators(self):
        #TODO who are the operators?
        template = 'registration_group_created.txt'
        context = {'group': self.group, 'user': self.user}
        operators_email = settings.MAINTEINANCE_EMAIL
        send_mail_template(template=template,
                           context=context,
                           email_from=settings.MAINTEINANCE_EMAIL,
                           to=operators_email)

    def save(self, *args, **kwargs):
        # Only notify the user when the GroupRegistration has successfully created
        if self.pk:
            self.notify_operators()
        super(GroupRegistration, self).save(*args, **kwargs)