from django import forms

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

