from django import forms
from django.core.exceptions import ValidationError

from .models import MgmtNetConf

class MgmtNetConfInlineForm(forms.ModelForm):
    """ Force admin create a new mgmt_net object """
    
    class Meta:
        model = MgmtNetConf

    def has_changed(self):
        """
        Should returns True if data differs from initial. 
        By always returning true even unchanged inlines will 
        get validated and saved.

        """
        return True


class MgmtNetDeviceModelForm(forms.ModelForm):
    """
    Validate management network configuration for a device
    (node, server, host) checking if tinc configuration is
    provided when tinc is the backend choosed.

    """
    def clean(self):
        super(MgmtNetDeviceModelForm, self).clean()
        mgm_prefix = 'mgmtnetworks-mgmtnetconf-content_type-object_id-0-'
        tinc_prefix = 'tinc-tinchost-content_type-object_id-0-'
        
        backend = self.data[mgm_prefix + 'backend']
        tinc_configured = self.data.get(tinc_prefix + 'pubkey', False)
        delete_tinc = bool(self.data.get(tinc_prefix + 'DELETE', False))
        
        if backend == 'tinc' and (not tinc_configured or delete_tinc):
            raise ValidationError("Please provide tinc backend configuration. "
                                  "Required because 'tinc' is choosed as "
                                  "backend for the management network.")
        return self.cleaned_data
