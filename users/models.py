import re

from django_extensions.db.fields import UUIDField
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from django.utils import timezone, six


# TODO add permission caching

class Permission(models.Model):
    ACTIONS = (
        ('view', 'View'),
        ('add', 'Add'),
        ('change', 'Change'),
        ('delete', 'Delete'),)
    
    content_type = models.ForeignKey(ContentType, related_name='testbedpermission_set')
    action = models.CharField(max_length=16, choices=ACTIONS)
    eval = models.CharField(max_length=256)
    eval_description = models.CharField(max_length=64, blank=True)
    
    def __unicode__(self):
        name =  "%s | %s | %s " % (
            six.text_type(self.content_type.app_label),
            six.text_type(self.content_type),
            six.text_type(self.action),)
        if self.eval_description:
            name += "| %s " % self.eval_description
        return name
    
    @classmethod
    def evaluate(cls, perm, user, obj):
        app_label = perm[:perm.index('.')]
        model = perm[perm.index('_')+1:]
        action = perm[perm.index('.')+1:perm.index('_')]
        perms = cls.objects.filter(role__userresearchgroup__user=user,
                                   content_type__app_label=app_label,
                                   content_type__model=model,
                                   action=action).distinct()
        if not obj:
            return perms.exists()
        for perm in perms:
            if eval(perm.eval):
                return  True
        return False

class Role(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=256, blank=True)
    permissions = models.ManyToManyField(Permission)
    
    # TODO each Research Group must have at least one PI.
    #       Add generic support like required=True
    
    def __unicode__(self):
        return self.name


class ResearchGroup(models.Model):
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=256, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=32)
    state = models.CharField(max_length=32)
    postal_code = models.PositiveIntegerField(blank=True, null=True)
    country = models.CharField(max_length=32) 
    url = models.URLField(blank=True)
    
    def __unicode__(self):
        return self.name


class UserResearchGroup(models.Model):
    user = models.ForeignKey('users.User')
    research_group = models.ForeignKey(ResearchGroup)
    roles = models.ManyToManyField(Role)
    
    class Meta:
        unique_together = ('user', 'research_group')
    
    def __unicode__(self):
        return self.research_group


class UserManager(BaseUserManager):
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


class User(AbstractBaseUser):
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
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True,
        help_text='Designates whether this user should be treated as '
                  'active. Unselect this instead of deleting accounts.')
    is_superuser = models.BooleanField(default=False,
        help_text='Designates that this user has all permissions without '
                    'explicitly assigning them.')
    date_joined = models.DateTimeField(default=timezone.now)
    pubkey = models.TextField('Public Key', unique=True, null=True, blank=True,
        help_text='A PEM-encoded RSA public key for this user (used by SFA).')
    # TODO add validator
    uuid = models.CharField(max_length=36, unique=True, blank=True, null=True,
        help_text='A universally unique identifier (UUID, RFC 4122) for this '
                  'user (used by SFA). This is optional, but once set to a valid '
                  'UUID it can not be changed.')
    research_groups = models.ManyToManyField(ResearchGroup, blank=True, 
        through=UserResearchGroup)
    
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
        Empty pubkey as NULL instead of empty string 
        """
        if self.pubkey is u'': self.pubkey = None
        super(User, self).clean()
    
    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def roles(self):
        return self.research_groups.all()
    
    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. 
        """
        if not self.is_active: 
            return False
        if self.is_superuser:
            return True
        return Permission.evaluate(perm, self, obj)
    
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
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return Permission.objects.filter(role__userresearchgroup__user=self,
                                         content_type__app_label=app_label).exists()
    
    @property
    def is_staff(self):
        """ All users can loggin to the admin interface """
        return True


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
