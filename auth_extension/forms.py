from django import forms

from common.widgets import ShowText


class UserProfileChangeForm(forms.ModelForm):
    """ Force display of UUID auto field """
    uuid = forms.CharField(widget=ShowText(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(UserProfileChangeForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.initial['uuid'] = instance.uuid
