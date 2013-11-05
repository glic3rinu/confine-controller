from django import forms
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from controller.forms.widgets import ShowText

from . import ResourcePlugin
from .models import Resource


class VerboseNameShowTextWidget(forms.Widget):
    def render(self, name, value, attrs):
        verbose_name = ResourcePlugin.get(value).verbose_name if value else force_text(value)
        final_value = u'%s<input type="hidden" name="%s" value="%s"/>' % (verbose_name, name, value)
        return mark_safe(final_value)
        
    def _has_changed(self, initial, data):
        return False


class ResourceInlineFormSet(generic.BaseGenericInlineFormSet):
    """ Provides initial resource values """
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if not instance.pk and 'data' not in kwargs:
            resources = ResourcePlugin.get_resources_for_producer(type(instance))
            total = len(resources)
            prefix = 'resources-resource-content_type-object_id-'
            initial_data = {
                prefix+'TOTAL_FORMS': unicode(total),
                prefix+'INITIAL_FORMS': u'0',
                prefix+'MAX_NUM_FORMS': unicode(total),
            }
            for num, resource in enumerate(resources):
                initial_data[prefix+'%d-name' % num] = resource.name
                initial_data[prefix+'%d-max_sliver' % num] = resource.max_sliver
                initial_data[prefix+'%d-dflt_sliver' % num] = resource.dflt_sliver
            kwargs['data'] = initial_data
        super(ResourceInlineFormSet, self).__init__(*args, **kwargs)



class ResourceReqInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ResourceReqInlineForm, self).__init__(*args, **kwargs)
        choices = []
        for resource in ResourcePlugin.get_resources_for_consumer(self.parent_model):
            choices.append((resource.name, resource.verbose_name))
        self.fields['name'] = forms.ChoiceField(choices=choices)
