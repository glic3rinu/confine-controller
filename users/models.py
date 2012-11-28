import re

from django.contrib.auth import models as auth_models
from django.core import validators
from django.db import models
from django.utils import timezone

from common.validators import UUIDValidator


class Group(models.Model):
    name = models.CharField(max_length=32, unique=True,
        help_text='A unique name for this group. A single non-empty line of '
                  'free-form text with no whitespace surrounding it. matching '
                  'the regular expression',
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'), 
                   'Enter a valid name.', 'invalid')])
    description = models.TextField(blank=True)
    # TODO Check these fields with Ivan
#    address = models.TextField()
#    city = models.CharField(max_length=32)
#    state = models.CharField(max_length=32)
#    postal_code = models.PositiveIntegerField(blank=True, null=True)
#    country = models.CharField(max_length=32) 
#    url = models.URLField(blank=True)
    uuid = models.CharField(max_length=36, unique=True, blank=True, null=True,
        help_text='A universally unique identifier (UUID, RFC 4122) for this '
                  'user (used by SFA). This is optional, but once set to a valid '
                  'UUID it can not be changed.', validators=[UUIDValidator])
    pubkey = models.TextField('Public Key', unique=True, null=True, blank=True,
        help_text='A PEM-encoded RSA public key for this user (used by SFA).')
    allow_nodes = models.BooleanField(default=False)
    allow_slices = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    
    def is_member(self, user):
        return Roles.objects.get(group=self, user=user).exists()
    
    def has_role(self, user, role):
        try: roles = Roles.objects.get(group=self, user=user)
        except Roles.DoesNotExist: 
            return False
        return roles.has_role(role)
    
    def has_roles(self, user, roles):
        try: group_roles = Roles.objects.get(group=self, user=user)
        except Roles.DoesNotExist: return False
        for role in roles:
            if group_roles.has_role(role): return True
        return False


class Roles(models.Model):
    # TODO prevent groups without admins
    user = models.ForeignKey('users.User')
    group = models.ForeignKey(Group)
    is_admin = models.BooleanField(default=False)
    is_technician = models.BooleanField(default=False)
    is_researcher = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'group')
        verbose_name_plural = 'roles'
    
    def __unicode__(self):
        return self.group
    
    def has_role(self, role):
        attr_map = {
            'technician': 'is_technician',
            'admin': 'is_admin',
            'researcher': 'is_researche'}
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
        u = self.create_user(username, email, password, **extra_fields)
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class User(auth_models.AbstractBaseUser):
    """
    Describes a person using the testbed.
    
    The implementation is based on auth.models.AbstractBaseUser, more:
    https://docs.djangoproject.com/en/dev/topics/auth/#customizing-the-user-model
    """
    username = models.CharField(max_length=30, unique=True,
        help_text='Required. 30 characters or fewer. Letters, numbers and '
                  '@/./+/-/_ characters',
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'), 
                    'Enter a valid username.', 'invalid')])
    email = models.EmailField('Email Address', max_length=255, unique=True)
    description = models.TextField(blank=True, 
        help_text='An optional free-form textual description of this user, it '
                  'can include URLs and other information.')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
#    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True,
        help_text='Designates whether this user should be treated as '
                  'active. Unselect this instead of deleting accounts.')
    is_superuser = models.BooleanField(default=False,
        help_text='Designates that this user has all permissions without '
                    'explicitly assigning them.')
    date_joined = models.DateTimeField(default=timezone.now)
    pubkey = models.TextField('Public Key', unique=True, null=True, blank=True,
        help_text='A PEM-encoded RSA public key for this user (used by SFA).')
    uuid = models.CharField(max_length=36, unique=True, blank=True, null=True,
        help_text='A universally unique identifier (UUID, RFC 4122) for this '
                  'user (used by SFA). This is optional, but once set to a valid '
                  'UUID it can not be changed.',
        validators=[UUIDValidator])
    groups = models.ManyToManyField(Group, blank=True, through=Roles)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    
    def __unicode__(self):
        return self.username
    
    def clean(self):
        """ 
        Empty pubkey and uuid as NULL instead of empty string 
        """
        if self.pubkey == '': self.pubkey = None
        if self.uuid == '': self.uuid = None
        super(User, self).clean()
    
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
    
    @property
    def is_staff(self):
        """ All users can loggin to the admin interface """
        return True
    
    @property
    def roles(self):
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
        if self.roles.intersection(roles): 
            return True
        return False


class AuthToken(models.Model):
    """ 
    A list of authentication tokens like SSH or other kinds of public keys or 
    X.509 certificates to be used for slivers or experiments. The exact valid 
    format depends on the type of token as long as it is non-empty and only 
    contains ASCII characters. (e.g. by using PEM encoding or other ASCII armour).
    """
    user = models.ForeignKey('users.User')
    data = models.TextField(help_text='Authentication token like SSH or other '
        'kinds of public keys or X.509 certificates to be used for slivers or '
        'experiments. The exact valid format depends on the type of token as '
        'long as it is non-empty and only contains ASCII characters '
        '(e.g. by using PEM encoding or other ASCII armour).')
    
    def __unicode__(self):
        return str(self.pk)

