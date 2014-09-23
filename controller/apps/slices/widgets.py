from django import forms
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from .models import Sliver


class IfacesSelect(forms.widgets.Select):
    """
    Custom SliverIfaces selector.
    Disables not allowed ifaces options showing the reason.
    
    """
    
    def __init__(self, attrs=None, choices=(), disabled_choices=[]):
        super(IfacesSelect, self).__init__(attrs, choices)
        self.disabled_choices = disabled_choices
    
    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        if option_value in self.disabled_choices:
            disabled_html = mark_safe(' disabled="disabled"')
            disabled_reason = Sliver.get_registered_ifaces()[option_value].DISABLED_MSG
            option_label = '%s (%s)' % (option_label, disabled_reason)
        else:
            disabled_html = ''
        return format_html('<option value="{0}"{1}{2}>{3}</option>',
                           option_value,
                           selected_html,
                           disabled_html,
                           force_text(option_label))

