from django import forms
from django.contrib.admin.templatetags.admin_list import _boolean_icon

from controller.forms.widgets import ShowText
from nodes.models import Node

from .helpers import state_value
from .models import Slice, Sliver


class SliceAdminForm(forms.ModelForm):
    class Meta:
        model = Slice


class SliverAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """ Improve user interface: form style and empty labels """
        # FIXME: Works but is NOT called: see SliverAdmin at admin.py
        super(SliverAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            sliver_state = state_value(self.instance.set_state)
            slice_state = state_value(self.instance.slice.set_state)
            if sliver_state > slice_state:
                self.fields['set_state'].widget.attrs = {'class': 'warning'}


class SliceSliversForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SliceSliversForm, self).__init__(*args, **kwargs)
        self.instance.node = self.node
        self.instance.slice = self.slice


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


class SliverIfaceInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """ Restrict parent FK to sliver.node """
        super(SliverIfaceInlineForm, self).__init__(*args, **kwargs)
        if 'parent' in self.fields:
            # readonly forms doesn't have model fields
            self.fields['parent'].queryset = self.node.direct_ifaces
            # Hook slice for future processing on iface.model_clean()
            self.instance.slice = self.slice
            # Remove unallowed iface types from choices
            queryset = Node.objects.filter(pk=self.node.id)
            choices = self.fields['type'].choices
            for iface_type, iface_object in Sliver.get_registered_ifaces().items():
                if not iface_object.is_allowed(self.slice, queryset):
                    choices = [choice for choice in choices if choice[0] != iface_type]
            self.fields['type'].choices = choices


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
            self.fields[iface_type] = forms.BooleanField(**kwargs)
