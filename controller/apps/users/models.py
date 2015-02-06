from django.contrib.auth import models as auth_models
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core import validators
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone

from controller.utils import send_email_template
from controller.core.validators import validate_ascii, validate_name
from controller.models.fields import NullableCharField, TrimmedCharField


class Group(models.Model):
    name = models.CharField(max_length=32, unique=True,
            help_text='A unique name for this group. A single non-empty line of '
                      'free-form text with no whitespace surrounding it.',
            validators=[validate_name])
    description = models.TextField(blank=True)
    allow_nodes = models.BooleanField(default=False,
            help_text='Whether nodes belonging to this group can be created or set '
                      'into production (false by default). Its value can only be '
                      'changed by testbed superusers.')
    allow_slices = models.BooleanField(default=False,
            help_text='Whether slices belonging to this group can be created or '
                      'instantiated (false by default). Its value can only be changed '
                      'by testbed superusers.')
    
    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """ Make sure nodes and slices are disabled if not allowed
            NOTE: state will be kept if current state is lower
        """
        original = Group.objects.get(pk=self.pk) if self.pk else False
        super(Group, self).save(*args, **kwargs)
        if not original: return
        if original.allow_slices and not self.allow_slices:
            from slices.models import Slice
            Slice.objects.filter(group=self, \
                set_state=Slice.START).update(set_state=Slice.DEPLOY)
        if original.allow_nodes and not self.allow_nodes:
            from nodes.models import Node
            Node.objects.filter(group=self, \
                set_state=Node.PRODUCTION).update(set_state=Node.SAFE)
    @property
    def admins(self):
        """ returns user queryset containing all group admins """
        return User.objects.filter_by_role(role=Roles.GROUP_ADMIN, roles__group=self)
    
    def is_member(self, user):
        return self.roles.filter(user=user).exists()
    
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
    
    def get_emails(self, role=False, roles=[]):
        if role:
            roles.append(role)
        users = User.objects.filter_by_role(roles=roles, roles__group=self)
        return users.values_list('email', flat=True)


class Roles(models.Model):
    SUPERUSER = 'superuser'
    GROUP_ADMIN = 'group_admin'
    NODE_ADMIN = 'node_admin'
    SLICE_ADMIN = 'slice_admin'
    
    user = models.ForeignKey('users.User', related_name='roles')
    group = models.ForeignKey(Group, related_name='roles')
    is_group_admin = models.BooleanField('group admin', default=False,
            help_text='Whether that user is an administrator in this group. An '
                      'administrator can manage slices and nodes belonging to the group'
                      ', members in the group and their roles, and the group itself.')
    is_node_admin = models.BooleanField('node admin (technician)', default=False,
            help_text='Whether that user is a node administrator in this group. '
                      'A node administrator can manage nodes belonging to the group.')
    is_slice_admin = models.BooleanField('slice admin (researcher)', default=False,
            help_text='Whether that user is a slice administrator in this group. '
                      'A slice administrator can manage slices belonging to the group.')
    
    class Meta:
        unique_together = ('user', 'group')
        verbose_name_plural = 'roles'
    
    def __unicode__(self):
        return unicode(self.group)
    
    def has_role(self, role):
        return getattr(self, 'is_%s' % role)


class UserManager(auth_models.BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not 'name' in extra_fields:
            raise ValueError("The 'name' field must be set for a new User")
        email = UserManager.normalize_email(email)
        user = self.model(username=username, email=email, is_active=True,
                is_superuser=False, last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password, **extra_fields):
        user = self.create_user(username, email, password, **extra_fields)
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    def filter_by_role(self, role=False, roles=[], *args, **kwargs):
        if role:
            roles.append(role)
        query = Q()
        for role in roles:
            query = query | Q(**{'roles__is_%s' % role: True})
        return self.filter(query).filter(*args, **kwargs).distinct()


class User(auth_models.AbstractBaseUser):
    """
    Describes a person using the testbed.
    
    The implementation is based on auth.models.AbstractBaseUser, more:
    https://docs.djangoproject.com/en/dev/topics/auth/#customizing-the-user-model
    """
    username = NullableCharField(max_length=30, null=True, blank=True,
            unique=True, db_index=True,
            help_text='Optional. A unique user alias for authentication. '
                      '30 characters or fewer. '
                      'Letters, numbers and ./+/-/_ characters.',
            # disallow '@' for avoiding foo_user.username == fake_user.email
            validators=[validators.RegexValidator('^[\w.+-]+$',
                        'Enter a valid username.', 'invalid')])
    email = models.EmailField('Email Address', max_length=255, unique=True,
            help_text='Required. A unique email for the user. '
                      'May be used for authentication.')
    description = models.TextField(blank=True, 
            help_text='An optional free-form textual description of this user, it '
                      'can include URLs and other information.')
    first_name = '' # fluent dashboard compatibility
    last_name = ''
    name = TrimmedCharField(max_length=60, unique=True, db_index=True,
            help_text='Required. A unique name for this user. A single non-empty '
                      'line of free-form text with no whitespace surrounding it.',
            validators=[validate_name])
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
    REQUIRED_FIELDS = ['email', 'name']
    
    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name
    
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
    
    def is_staff(self):
        """ All users can log in to the admin interface """
        return True
    
    def email_user(self, subject, message, from_email=None):
        """ Used for django-registration """
        send_mail(subject, message, from_email, [self.email])
    
    @property
    def role_set(self):
        roles = set()
        for role in Roles.objects.filter(user=self):
            if role.is_group_admin:
                roles.update([Roles.GROUP_ADMIN])
            if role.is_node_admin:
                roles.update([Roles.NODE_ADMIN])
            if role.is_slice_admin:
                roles.update([Roles.SLICE_ADMIN])
            if len(roles) > 3:
                break
        if self.is_superuser:
            roles.update([Roles.SUPERUSER])
        return roles
    
    def has_roles(self, roles):
        if self.role_set.intersection(roles):
            return True
        return False
    
    def has_role(self, role):
        return self.has_roles((role,))
    
    def is_member(self, group):
        return self.roles.filter(group=group).exists()
    
    @classmethod
    def get_emails(cls, role=False, roles=[]):
        if role:
            roles.append(role)
        users = cls.objects.filter_by_role(roles=roles)
        return users.values_list('email', flat=True)


class AuthToken(models.Model):
    """ 
    A list of authentication tokens like SSH or other kinds of public keys or 
    X.509 certificates to be used for slivers or experiments. The exact valid 
    format depends on the type of token as long as it is non-empty and only 
    contains ASCII characters. (e.g. by using PEM encoding or other ASCII armour).
    """
    user = models.ForeignKey('users.User', related_name='auth_tokens')
    data = models.TextField(validators=[validate_ascii],
            help_text='Authentication token like SSH or other kinds of public keys '
                      'or X.509 certificates to be used for slivers or experiments. '
                      'The exact valid format depends on the type of token as long '
                      'as it is non-empty and only contains ASCII characters '
                      '(e.g. by using PEM encoding or other ASCII armour).')
    
    class Meta:
        verbose_name = 'authentication token'
        verbose_name_plural = 'authentication tokens'
    
    def __unicode__(self):
        return unicode(self.pk)
    
    def clean(self):
        super(AuthToken, self).clean()
        self.data = self.data.strip()


class JoinRequest(models.Model):
    """
    This model's purpose is to store data temporaly for join the group.
    
    An user can request to join into a group in two main scenaries:
    1. While the registration: chooses the group(s)
    2. A registered user: can request to join a group(s)
    
    Once the request is created, the group's admin have to check it
    accepting or refusing it.
    """
    user = models.ForeignKey(User, related_name='join_requests')
    group = models.ForeignKey(Group, related_name='join_requests')
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'group')
    
    def __unicode__(self):
        return '#%s' % self.pk
    
    def send_creation_email(self, site):
        context = { 'request': self, 'site': site }
        to = self.group.get_emails(role=Roles.GROUP_ADMIN)
        template = 'users/created_join_request.email'
        send_email_template(template=template, context=context, to=to)
    
    def send_approval_email(self, site):
        context = { 'request': self, 'site': site }
        template = 'users/accepted_join_request.email'
        to = self.user.email
        send_email_template(template=template, context=context, to=to)
    
    def send_rejection_email(self, site):
        context = { 'request': self, 'site': site }
        template = 'users/rejected_join_request.email'
        to = self.user.email
        send_email_template(template=template, context=context, to=to)
    
    def accept(self, roles=[]):
        """
        The admin accepts the user's request to join.
        The user is added to the group and the request is deleted
        """
        roles_kwargs = dict(('is_%s' % role, True) for role in roles)
        Roles.objects.create(user=self.user, group=self.group, **roles_kwargs)
        self.delete()
    
    def reject(self):
        """
        The admin refuse the user's request to join.
        The request is deleted
        """
        self.delete()


class ResourceRequest(models.Model):
    """
    Implements a system to manage the groups resources.
    A group admin can create a request asking for enable
    resources for the group (e.g. slices, nodes)
    """
    RESOURCES = (
        ('nodes', 'Nodes'),
        ('slices', 'Slices'))
    
    group = models.ForeignKey(Group, related_name='resource_requests')
    resource = models.CharField(max_length=16, choices=RESOURCES)
    
    def send_creation_email(self, site):
        context = { 'request': self, 'site': site }
        to = User.objects.filter(is_superuser=True).values_list('email', flat=True)
        template = 'users/created_resource_request.email'
        send_email_template(template=template, context=context, to=to)
    
    def send_approval_email(self, site):
        context = { 'request': self, 'site': site }
        template = 'users/accepted_resource_request.email'
        to = self.group.get_emails(role=Roles.GROUP_ADMIN)
        send_email_template(template=template, context=context, to=to)
    
    def accept(self):
        """Accept the request updating the group properties
        according to the requests info"""
        setattr(self.group, 'allow_%s' % self.resource, True)
        self.group.save()
        self.delete()


# SIGNALS
# FIXME(santiago): prevent groups without group admin.
# The following code is too restrictive and disallow group deletion!
#@receiver(pre_delete, sender=User)
#def prevent_group_without_admin_user(sender, instance, **kwargs):
#    for rol in instance.roles.filter(is_group_admin=True):
#        prevent_group_without_admin_role(sender, rol, **kwargs)
#
#
#@receiver(pre_delete, sender=Roles)
#def prevent_group_without_admin_role(sender, instance, **kwargs):
#    if not instance.group.roles.filter(is_group_admin=True).exclude(user=instance.user).exists():
#        raise PermissionDenied('The group must have at least one admin.')
