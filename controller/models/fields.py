from django.db import models
from django.core import exceptions
from django.utils.text import capfirst

from controller.core.validators import validate_cert, validate_rsa_pubkey
from controller.forms.fields import MultiSelectFormField
from controller.utils.apps import is_installed


class MultiSelectField(models.Field):
    """ http://djangosnippets.org/snippets/1200/ """
    __metaclass__ = models.SubfieldBase
    
    def get_internal_type(self):
        return "CharField"
    
    def get_choices_default(self):
        return self.get_choices(include_blank=False)
    
    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)
    
    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'choices': self.choices }
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)
    
    def get_prep_value(self, value):
        return value
    
    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)
    
    def get_default(self):
        """Return default string to array"""
        value = super(MultiSelectField, self).get_default()
        return [x.strip() for x in value.split(',')] if value else value
    
    def to_python(self, value):
        if value is not None:
            return value if isinstance(value, list) else value.split(',')
        return ''
    
    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname=name, choicedict=dict(self.choices): \
                ",".join([ choicedict.get(value, value) for value in getattr(self, fieldname) ])
            setattr(cls, 'get_%s_display' % self.name, func)
    
    def validate(self, value, model_instance):
        arr_choices = self.get_choices_selected(self.get_choices_default())
        for opt_select in value:
            if (opt_select not in arr_choices):  # the int() here is for comparing with integer choices
                raise exceptions.ValidationError(self.error_messages['invalid_choice'] % value)
        return
    
    def get_choices_selected(self, arr_choices=''):
        if not arr_choices:
            return False
        list = []
        for choice_selected in arr_choices:
            list.append(choice_selected[0])
        return list
    
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


class RSAPublicKeyField(models.TextField):
    default_validators = [validate_rsa_pubkey]
    
    def get_db_prep_value(self, value, connection=None, prepared=False):
        """Remove carriage return to avoid problems on API representation."""
        return value.replace('\r\n', '\n').strip() if value else None
    
    # TODO to_python returns an rsa key?


class URIField(models.URLField):
    def __init__(self, *args, **kwargs):
        kwargs['unique'] = kwargs.get('unique', True)
        kwargs['null'] = kwargs.get('null', True)
        return super(URIField, self).__init__(*args, **kwargs)
    
    def get_prep_value(self, value):
        return value or None


class NullableCharField(models.CharField):
     def get_db_prep_value(self, value, connection=None, prepared=False):
         return value or None


class NullableTextField(models.TextField):
     def get_db_prep_value(self, value, connection=None, prepared=False):
         return value or None


class PEMCertificateField(models.TextField):
    """X.509 PEM-encoded certificate."""
    default_validators = [validate_cert]
    
    def get_db_prep_value(self, value, connection=None, prepared=False):
        """Remove carriage return to avoid problems on API representation."""
        return value.replace('\r\n', '\n').strip() if value else None


class TrimmedCharField(models.CharField):
    """ Remove trailing spaces """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value: value = value.strip()
        return super(TrimmedCharField, self).to_python(value)

if is_installed('south'):
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^controller\.models\.fields\.MultiSelectField"])
    add_introspection_rules([], ["^controller\.models\.fields\.RSAPublicKeyField"])
    add_introspection_rules([], ["^controller\.models\.fields\.URIField"])
    add_introspection_rules([], ["^controller\.models\.fields\.NullableCharField"])
    add_introspection_rules([], ["^controller\.models\.fields\.NullableTextField"])
    add_introspection_rules([], ["^controller\.models\.fields\.PEMCertificateField"])
    add_introspection_rules([], ["^controller\.models\.fields\.TrimmedCharField"])

