"""
Forms for group registration.

"""


from users.models import Group
from django import forms


class GroupRegistrationForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'description')

