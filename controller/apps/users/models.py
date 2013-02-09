from django.contrib.auth import models as auth_models
from django.core.mail import send_mail
from django.core import validators
from django.db import models
from django.utils import timezone

from controller.utils import send_mail_template
from controller.core.validators import validate_ascii


class Group(models.Model):
    name = models.CharField(max_length=32, unique=True,
        help_text='A unique name for this group. A single non-empty line of '
                  'free-form text with no whitespace surrounding it. matching '
                  'the regular expression',
        validators=[validators.RegexValidator('^[\w.@+-]+$', 
                   'Enter a valid name.', 'invalid')])
    description = models.TextField(blank=True)
    # used when someone send a request to create a group
#    is_approved = models.BooleanField(default=False,
#        help_text='Designates if a group has been approved by the operations '
#                  'team. When someone sends a request, a group pending of '
#                  'be approved is created.')
    allow_nodes = models.BooleanField(default=False,
        help_text='Whether nodes belonging to this group can be created or set '
                  'into production (false by default). Its value can only be '
                  'changed by testbed superusers.')
    allow_slices = models.BooleanField(default=False,
        help_text='Whether slices belonging to this group can be created or '
                  'instantiated (false by default). Its value can only be changed '
                  'by testbed superusers.')
    
    def __unicode__(self):
        return self.name
    
    @property
    def admins(self):
        """ return user queryset containing all admins """
        admins = User.objects.filter(roles__is_admin=True, roles__group=self)
        if not admins.exists():
            raise Roles.DoesNotExist("Group Error: the group %s doesn't have any admin." % self)
        return admins
    
    def is_member(self, user):
        return Roles.objects.filter(group=self, user=user).exists()
    
    def has_role(self, user, role):
        return self.has_roles(user, (role,))
    
    def has_roles(self, user, roles):
        try:
            group_roles = Roles.objects.get(group=self, user=user)
        except Roles.DoesNotExist:
            return False
        for role in roles:
            if group_roles.has_role(role):
                return True
        return False
    
    def get_admin_emails(self):
        return self.admins.values_list('email', flat=True)


class Roles(models.Model):
    # TODO prevent groups without admins
    user = models.ForeignKey('users.User', related_name='roles')
    group = models.ForeignKey(Group, related_name='roles')
    is_admin = models.BooleanField(default=False,
        help_text='Whether that user is an administrator in this group. An '
                  'administrator can manage slices and nodes belonging to the group'
                  ', members in the group and their roles, and the group itself.')
    is_technician = models.BooleanField(default=False,
        help_text='Whether that user is a technician in this group. A technician '
                  'can manage nodes belonging to the group.')
    is_researcher = models.BooleanField(default=False,
        help_text='Whether that user is a researcher in this group. A researcher '
                  'can manage slices belonging to the group.')
    
    class Meta:
        unique_together = ('user', 'group')
        verbose_name_plural = 'roles'
    
    def __unicode__(self):
        return str(self.group)
    
    def has_role(self, role):
        attr_map = {
            'technician': 'is_technician',
            'admin': 'is_admin',
            'researcher': 'is_researcher'}
        return getattr(self, attr_map[role])


class UserManager(auth_models.BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = UserManager.normalize_email(email)
        user = self.model(username=username, email=email, is_active=True, 
                          is_superuser=False, last_login=now, date_joined=now, 
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password, **extra_fields):
        user = self.create_user(username, email, password, **extra_fields)
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(auth_models.AbstractBaseUser):
    """
    Describes a person using the testbed.
    
    The implementation is based on auth.models.AbstractBaseUser, more:
    https://docs.djangoproject.com/en/dev/topics/auth/#customizing-the-user-model
    """
    username = models.CharField(max_length=30, unique=True,
        help_text='Required. 30 characters or fewer. Letters, numbers and '
                  '@/./+/-/_ characters',
        validators=[validators.RegexValidator('^[\w.@+-]+$', 
                    'Enter a valid username.', 'invalid')])
    email = models.EmailField('Email Address', max_length=255, unique=True)
    description = models.TextField(blank=True, 
        help_text='An optional free-form textual description of this user, it '
                  'can include URLs and other information.')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True,
        help_text='Designates whether this user should be treated as '
                  'active. Unselect this instead of deleting accounts.')
    is_superuser = models.BooleanField(default=False,
        help_text='Designates that this user has all permissions without '
                  'explicitly assigning them.')
    date_joined = models.DateTimeField(default=timezone.now)
    groups = models.ManyToManyField(Group, blank=True, through=Roles, related_name='users')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    
    def __unicode__(self):
        return self.username
    
    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
    
    def get_short_name(self):
        return self.first_name
    
    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        
        # Otherwise we need to check the backends.
        return auth_models._user_has_perm(self, perm, obj)
    
    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        return auth_models._user_has_module_perms(self, app_label)
    
    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        # TODO Deprecate?
        send_mail(subject, message, from_email, [self.email])
    
    def is_staff(self):
        """ All users can loggin to the admin interface """
        return True
    
    @property
    def role_set(self):
        roles = set()
        for role in Roles.objects.filter(user=self):
            if role.is_admin:
                roles.update(['admin'])
            if role.is_technician:
                roles.update(['technician'])
            if role.is_researcher:
                roles.update(['researcher'])
            if len(roles) > 3:
                break
        if self.is_superuser:
            roles.update(['superuser'])
        
        return roles
    
    def has_roles(self, roles):
        if self.role_set.intersection(roles):
            return True
        return False


class AuthToken(models.Model):
    """ 
    A list of authentication tokens like SSH or other kinds of public keys or 
    X.509 certificates to be used for slivers or experiments. The exact valid 
    format depends on the type of token as long as it is non-empty and only 
    contains ASCII characters. (e.g. by using PEM encoding or other ASCII armour).
    """
    user = models.ForeignKey('users.User', related_name='auth_tokens')
    data = models.TextField(help_text='Authentication token like SSH or other '
        'kinds of public keys or X.509 certificates to be used for slivers or '
        'experiments. The exact valid format depends on the type of token as '
        'long as it is non-empty and only contains ASCII characters '
        '(e.g. by using PEM encoding or other ASCII armour).',
        validators=[validate_ascii])
    
    class Meta:
        verbose_name = 'Authentication Token'
        verbose_name_plural = 'Authentication Tokens'
    
    def __unicode__(self):
        return str(self.pk)


class JoinRequest(models.Model):
    """
    This model's purpose is to store data temporaly for join the group.
    
    An user can request to join into a group in two main scenaries:
    1. While the registration: chooses the group(s)
    2. A registered user: can request to join a group(s)
    
    Once the request is created, the group's admin have to check it
    accepting or refusing it.
    """
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'group')
    
    def __unicode__(self):
        return '#%s' % self.pk
    
    def save(self, *args, **kwargs):
        if self.pk:
            # Notify admins that a new join request is created
            admins = self.group.get_admin_emails()
            self.notify(template='users/created_join_request.email', to=admins)
        super(JoinRequest, self).save(*args, **kwargs)
    
    def accept(self, roles=[]):
        """
        The admin accepts the user's request to join.
        The user is added to the group and the request is deleted
        """
        roles_kwargs = dict( ('is_%s' % role, True) for role in roles )
        Roles.objects.create(user=self.user, group=self.group, **roles_kwargs)
        self.notify(template='users/accepted_join_request.email',
                    to=self.user.email)
        self.delete()
    
    def reject(self):
        """
        The admin refuse the user's request to join.
        The request is deleted
        """
        self.notify(template='users/rejected_join_request.email',
                    to=self.user.email)
        self.delete()
    
    def ignore(self, *args, **kwargs):
        """ Just delete it without sending notifications """
        self.delete(*args, **kwargs)
    
    def notify(self, template, to):
        context = {'group': self.group}
        send_mail_template(template=template, context=context, to=to)
