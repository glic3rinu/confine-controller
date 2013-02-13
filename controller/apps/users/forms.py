from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.template.defaultfilters import mark_safe

from controller.forms.fields import MultiSelectFormField

from users.models import User, JoinRequest, ResourceRequest


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'email')
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    
    class Meta:
        model = User
    
    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class RolesFormSet(forms.models.BaseInlineFormSet):
    """ At least on admin per group """
    # TODO: ensure this also when deleting a user (more triky though)
    def clean(self):
        super(RolesFormSet, self).clean()
        # Only checking in change forms
        if self.__obj__ is not None:
            for form in self.forms:
                if form.cleaned_data.get('is_admin'):
                    return
            raise ValidationError('The group must have at least one admin')


class GroupAdminForm(forms.ModelForm):
    """ Provides support for requesting resources on groups """
    request_nodes = forms.BooleanField(label='Request nodes', required=False,
        help_text='Whether nodes belonging to this group can be created or set '
                  'into production (false by default). Its value can only be '
                  'changed by testbed superusers.')
    request_slices = forms.BooleanField(label='Request slices', required=False,
        help_text='Whether slices belonging to this group can be created or '
                  'instantiated (false by default). Its value can only be changed '
                  'by testbed superusers.')

    class Meta:
        # TODO this is redundant if is_approved is deprecated
        exclude = ('is_approved',)

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        group = kwargs.get('instance', False)
        if group:
            for resource, verbose in ResourceRequest.RESOURCES:
                has_request = group.resource_requests.filter(resource=resource).exists()
                if 'request_%s' % resource in self.fields:
                    self.fields['request_%s' % resource].initial = has_request
                # show a message to the operators if exists a resource request
                elif has_request and 'allow_%s' % resource in self.fields:
                    label = mark_safe("%s <span class='help' style='color:black'>"
                        "(resource requested by the admin of the group)</span>"
                        % self.fields['allow_%s' % resource].label)
                    self.fields['allow_%s' % resource].label = label

    def save(self, commit=True):
        group = super(GroupAdminForm, self).save(commit=commit)
        if not commit:
            # for a new group force to save it before creating resource requests
            group.save()
        for resource, verbose in ResourceRequest.RESOURCES:
            if self.cleaned_data.get('request_%s' % resource):
                # Create request if needed
                ResourceRequest.objects.get_or_create(resource=resource, group=group)
            else:
                # Delete request if exists
                group.resource_requests.filter(resource=resource).delete()
            if self.cleaned_data.get('allow_%s' % resource):
                # Supperuser has enabled the resource
                # handling through the request if needed
                request = group.resource_requests.filter(resource=resource)
                if request:
                    request.accept()
        return group


class JoinRequestForm(forms.ModelForm):
    ACTIONS = (
        ('accept', 'Accept'),
        ('reject', 'Reject'),
        ('ignore', 'Ignore'))
    ROLES = (
        ('admin', 'Admin'),
        ('technician', 'Technician'),
        ('researcher', 'Researcher'))
    
    action = MultiSelectFormField(label='Action', choices=ACTIONS, required=False)
    roles = MultiSelectFormField(label='Roles', choices=ROLES, required=False)
    
    class Meta:
        model = JoinRequest
    
    def clean_action(self):
        actions = self.cleaned_data.get('action')
        if len(actions) > 1:
            raise ValidationError('Select only one action')
        return actions[0] if len(actions) == 1 else ''
    
    def save(self, commit=True):
        action = self.cleaned_data.get('action')
        roles = self.cleaned_data.get('roles')
        if roles and action in ['accept', '']:
            # Accept if explicit and also when a role is selected without any action
            self.instance.accept(roles=roles)
        elif action:
            getattr(self.instance, action)()
