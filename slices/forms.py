from common.widgets import ShowText
from django import forms
from slices.models import Slice


class SliceAdminForm(forms.ModelForm):
    """ Provide vlan_nr as a request checkbox """
    request_vlan = forms.BooleanField(label='Request VLAN', initial=False, required=False, 
        help_text="""A VLAN number allocated to this slice by the server.""")

    class Meta:
        model = Slice

    def __init__(self, *args, **kwargs):
        super(SliceAdminForm, self).__init__(*args, **kwargs)
        if not 'instance' in kwargs:
            self.fields['vlan_nr'] = self.fields['request_vlan'] 
        else:
            instance = kwargs['instance']
            if instance.set_state == 'register' and instance.vlan_nr == -1:
                self.fields['vlan_nr'] = self.fields['request_vlan']
                self.initial['vlan_nr'] = True
            elif instance.set_state == 'register':
                self.fields['vlan_nr'] = self.fields['request_vlan']
                self.initial['vlan_nr'] = False
            else:
                self.fields['vlan_nr'].widget = ShowText()
                self.fields['vlan_nr'].widget.attrs['readonly'] = True
        
    def clean_vlan_nr(self):
        vlan_nr = self.cleaned_data['vlan_nr']
        if vlan_nr == True: return -1
        return vlan_nr

