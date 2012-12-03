from django import forms
from django.utils.safestring import mark_safe


class ShowText(forms.Widget):
    def render(self, name, value, attrs):
        if hasattr(self, 'initial'):
            value = self.initial
        if self.bold: 
            final_value = u'<b>%s</b>' % (value)
        else:
            final_value = value
        if self.warning:
            final_value = u'<ul class="messagelist"><li class="warning">%s</li></ul>' %(final_value)
        if self.hidden:
            final_value = u'%s<input type="hidden" name="%s" value="%s"/>' % (final_value, name, value)
        return mark_safe(final_value)
            
    def __init__(self, *args, **kwargs):
        for kwarg in ['bold', 'warning', 'hidden']:
            setattr(self, kwarg, kwargs.pop(kwarg, False))
        super(ShowText, self).__init__(*args, **kwargs)
        
    def _has_changed(self, initial, data):
        return False
