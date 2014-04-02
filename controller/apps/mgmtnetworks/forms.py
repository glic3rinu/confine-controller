from django.forms.models import ModelForm

class MgmtNetConfInlineForm(ModelForm):
    """ Force admin create a new mgmt_net object """

    def has_changed(self):
        """
        Should returns True if data differs from initial. 
        By always returning true even unchanged inlines will 
        get validated and saved.

        """
        return True
