from django import forms
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.core.exceptions import ValidationError

from controller.forms.widgets import ShowText
from nodes.models import Node

from .helpers import state_value
from .models import SliverDefaults, Sliver
from .widgets import IfacesSelect


class SliverDefaultsInlineForm(forms.ModelForm):
    class Meta:
        model = SliverDefaults
        fields = ('template', 'set_state', 'data', 'data_uri', 'data_sha256',
                  'instance_sn')
    
    def clean(self):
        """Clean _uri when uploading a file"""
        cleaned_data = super(SliverDefaultsInlineForm, self).clean()
        for field_name in ('data',):
            if cleaned_data.get(field_name):
                cleaned_data[field_name + "_uri"] = ''
        return cleaned_data
    
    def has_changed(self):
        """
        Hack to force form validation.
        (avoid create an slice without sliver_defaults)
        
        """
        return True


class SliverAdminForm(forms.ModelForm):
    """
    Used when sliver showed directly (slice independent)
    e.g. /admin/sliver/1
    """
    def __init__(self, *args, **kwargs):
        super(SliverAdminForm, self).__init__(*args, **kwargs)
        # warn visually on sliver state override by slice state
        if self.instance:
            sliver_state = state_value(self.instance.set_state)
            slice_state = state_value(self.instance.slice.set_state)
            if sliver_state > slice_state and 'set_state' in self.fields:
                self.fields['set_state'].widget.attrs = {'class': 'warning'}
    
    def clean(self):
        """Clean _uri when uploading a file"""
        cleaned_data = super(SliverAdminForm, self).clean()
        for field_name in ('data',):
            if cleaned_data.get(field_name):
                cleaned_data[field_name + "_uri"] = ''
        return cleaned_data


class SliceSliversForm(forms.ModelForm):
    """
    Used when sliver showed via its slice (url nested)
    e.g. /admin/slice/1/sliver/1
    """
    def __init__(self, *args, **kwargs):
        super(SliceSliversForm, self).__init__(*args, **kwargs)
        self.instance.node = self.node
        self.instance.slice = self.slice
        # warn visually on sliver state override by slice state
        if self.instance:
            sliver_state = state_value(self.instance.set_state)
            slice_state = state_value(self.instance.slice.set_state)
            if sliver_state > slice_state and 'set_state' in self.fields:
                self.fields['set_state'].widget.attrs = {'class': 'warning'}
    
    def clean(self):
        """Clean _uri when uploading a file"""
        cleaned_data = super(SliceSliversForm, self).clean()
        for field_name in ('data',):
            if cleaned_data.get(field_name):
                cleaned_data[field_name + "_uri"] = ''
        return cleaned_data


class SliverIfaceInlineFormSet(forms.models.BaseInlineFormSet):
    """ Provides initial Direct ifaces """
    def __init__(self, *args, **kwargs):
        if not kwargs['instance'].pk and 'data' not in kwargs:
            all_ifaces = Sliver.get_registered_ifaces()
            auto_ifaces = [ (t,o) for t,o in all_ifaces.items()
                            if o.AUTO_CREATE or o.CREATE_BY_DEFAULT ]
            total = len(auto_ifaces)
            initial_data = {
                'interfaces-TOTAL_FORMS': unicode(total),
                'interfaces-INITIAL_FORMS': u'0',
                'interfaces-MAX_NUM_FORMS': u'',}
            for num, iface in enumerate(auto_ifaces):
                iface_type, iface_object = iface
                initial_data['interfaces-%d-name' % num] = iface_object.DEFAULT_NAME
                initial_data['interfaces-%d-type' % num] = iface_type
            kwargs['data'] = initial_data
        super(SliverIfaceInlineFormSet, self).__init__(*args, **kwargs)
    
    def clean(self):
        """Check that one interface of type private has been defined."""
        super(SliverIfaceInlineFormSet, self).clean()
        priv_ifaces = 0
        for form in self.forms:
            if form.cleaned_data.get('type', '') == 'private' and not form.cleaned_data.get('DELETE', False):
                priv_ifaces += 1
            if priv_ifaces > 1:
                raise ValidationError('There can only be one interface of type private.')
        if priv_ifaces == 0:
            raise ValidationError('There must exist one interface of type private.')


class SliverIfaceInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """ Restrict parent FK to sliver.node """
        super(SliverIfaceInlineForm, self).__init__(*args, **kwargs)
        if 'parent' in self.fields:
            # readonly forms doesn't have model fields
            self.fields['parent'].queryset = self.node.direct_ifaces
            # Hook slice for future processing on iface.model_clean()
            self.instance.slice = self.slice
            # Mark as disabled unallowed iface types from choices
            queryset = Node.objects.filter(pk=self.node.id)
            choices = self.fields['type'].choices
            disabled_choices = []
            for iface_type, iface_object in Sliver.get_registered_ifaces().items():
                if not iface_object.is_allowed(self.slice, queryset):
                    disabled_choices.append(iface_type)
            self.fields['type'].widget = IfacesSelect(choices=choices,
                                            disabled_choices=disabled_choices)


class SliverIfaceBulkForm(forms.Form):
    """ Display available ifaces on add sliver bulk action """
    def __init__(self, slice, queryset, *args, **kwargs):
        super(SliverIfaceBulkForm, self).__init__(*args, **kwargs)
        for iface_type, iface_object in Sliver.get_registered_ifaces().items():
            kwargs = {
                'label': iface_type,
                'required': False,
                'help_text': iface_object.__doc__.strip() }
            if iface_object.ALLOW_BULK and iface_object.is_allowed(slice, queryset):
                if iface_object.AUTO_CREATE:
                    kwargs['initial'] = _boolean_icon(True)
                    kwargs['widget'] = ShowText()
                if iface_object.CREATE_BY_DEFAULT:
                    kwargs['initial'] = True
            else:
                kwargs['initial'] = _boolean_icon(False)
                kwargs['widget'] = ShowText()
                kwargs['label'] += ' (%s)' % iface_object.VERBOSE_DISABLED_MSG
            self.fields[iface_type] = forms.BooleanField(**kwargs)
