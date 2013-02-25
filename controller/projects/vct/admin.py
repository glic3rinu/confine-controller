import os

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

from controller.utils import is_installed


class LocalFileField(forms.fields.FileField):
    def to_python(self, data):
        if data in validators.EMPTY_VALUES:
            return None
        return data


if is_installed('firmware'):
    from firmware.admin import BaseImageInline
    from firmware.models import BaseImage
    
    class VCTBaseImageInlineForm(forms.ModelForm):
        image = LocalFileField(required=False)
        
        def __init__(self, *args, **kwargs):
            super(VCTBaseImageInlineForm, self).__init__(*args, **kwargs)
            field = BaseImage._meta.get_field_by_name('image')[0]
            path = os.path.join(field.storage.location, field.upload_to)
            choices = ( (name, name) for name in os.listdir(path) if name.endswith('.img.gz') )
            self.fields['image'].widget = forms.widgets.Select(choices=choices)
    
    BaseImageInline.form = VCTBaseImageInlineForm

