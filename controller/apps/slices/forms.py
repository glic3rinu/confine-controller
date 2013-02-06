from django import forms

from controller.forms.widgets import ShowText

from .models import Slice, Sliver


class SliceAdminForm(forms.ModelForm):
    """ 
    Provide vlan_nr form field in two flavours, depending on slice state:
        1) If state is register: checkbox
        2) If state is not register: read only integer
    """
    # TODO this is not coding, this is hacking, please refactor this shit.
    request_vlan = forms.BooleanField(label='Request VLAN', initial=False, required=False, 
        help_text='VLAN number allocated to this slice by the server.')
    
    class Meta:
        model = Slice
    
    def __init__(self, *args, **kwargs):
        super(SliceAdminForm, self).__init__(*args, **kwargs)
        # read only views doens't have fields
        if 'vlan_nr' in self.fields:
            if not 'instance' in kwargs:
                self.fields['vlan_nr'] = self.fields['request_vlan'] 
            else:
                instance = kwargs['instance']
                if instance.set_state == Slice.REGISTER and instance.vlan_nr == -1:
                    self.fields['vlan_nr'] = self.fields['request_vlan']
                    self.initial['vlan_nr'] = True
                elif instance.set_state == Slice.REGISTER:
                    self.fields['vlan_nr'] = self.fields['request_vlan']
                    self.initial['vlan_nr'] = False
                else:
                    self.fields['vlan_nr'].widget = ShowText()
                    self.fields['vlan_nr'].widget.attrs['readonly'] = True
        
    def clean_vlan_nr(self):
        """ Return -1 if user requests vlan_nr """
        vlan_nr = self.cleaned_data['vlan_nr']
        if isinstance(vlan_nr, bool):
            if vlan_nr: return -1
        return vlan_nr


class SliverIfaceInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """ Restrict parent FK to sliver.node """
        super(SliverIfaceInlineForm, self).__init__(*args, **kwargs)
        if 'parent' in self.fields:
            # readonly forms doesn't have model fields
            # TODO handle this on the permission application?
            self.fields['parent'].queryset = self.node.direct_ifaces


class SliverIfaceBulkForm(forms.Form):
    """ Display available ifaces on add sliver bulk action """
    def __init__(self, *args, **kwargs):
        super(SliverIfaceBulkForm, self).__init__(*args, **kwargs)
        for iface_type in Sliver.get_registred_iface_types():
            iface_type = iface_type[0]
            iface = Sliver.get_registred_iface(iface_type)
            if iface.ALLOW_BULK:
                self.fields[iface_type] = forms.BooleanField(label=iface_type, 
                    required=False, help_text=iface.__doc__.strip())

