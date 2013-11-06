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
            prefix = kwargs['prefix']
            initial_data = {
                prefix+'-TOTAL_FORMS': unicode(total),
                prefix+'-INITIAL_FORMS': u'0',
                prefix+'-MAX_NUM_FORMS': unicode(total),
            }
            for num, resource in enumerate(resources):
                initial_data[prefix+'-%d-name' % num] = resource.name
                initial_data[prefix+'-%d-max_sliver' % num] = resource.max_sliver
                initial_data[prefix+'-%d-dflt_sliver' % num] = resource.dflt_sliver
            kwargs['data'] = initial_data
        super(ResourceInlineFormSet, self).__init__(*args, **kwargs)


class ResourceReqInlineFormSet(generic.BaseGenericInlineFormSet):
    """ Provides initial resource values """
    def __init__(self, *args, **kwargs):
        if not args and not 'data' in kwargs:
            instance = kwargs.get('instance')
            initial_data = {}
            prefix = kwargs['prefix']
            available = ResourcePlugin.get_resources_for_consumer(type(instance))
            existing = instance.resources.all() if instance.pk else []
            total = len(available)
            initial_data = {
                prefix+'-TOTAL_FORMS': unicode(total),
                prefix+'-MAX_NUM_FORMS': unicode(total),
            }
            availables = []
            existings = []
            for availableres in available:
                exists = False
                for existingres in existing:
                    if availableres.name == existingres.name:
                        exists = True
                        existings.append(existingres)
                if not exists:
                    availables.append(availableres)
            for num, resource in enumerate(existings):
                initial_data[prefix+'-%d-id' % num] = resource.id
                initial_data[prefix+'-%d-name' % num] = resource.name
                initial_data[prefix+'-%d-req' % num] = resource.req
                initial_data[prefix+'-%d-unit' % num] = resource.unit
            for num, resource in enumerate(availables, len(existings)):
                initial_data[prefix+'-%d-name' % num] = resource.name
                initial_data[prefix+'-%d-unit' % num] = resource.unit
                kwargs['data'] = initial_data
            initial_data[prefix+'-INITIAL_FORMS'] = unicode(len(existings))
        super(ResourceReqInlineFormSet, self).__init__(*args, **kwargs)
    
    def save_new(self, form, commit=True):
        """ Do not save empty objects """
        if not form.cleaned_data['req']:
            return super(ResourceReqInlineFormSet, self).save_new(form, commit=False)
        return super(ResourceReqInlineFormSet, self).save_new(form, commit=commit)
    
    def save_existing(self, form, instance, commit=True):
        """ Remove empty objects """
        if not form.cleaned_data['req']:
            instance.delete()
            return instance
        return super(ResourceReqInlineFormSet, self).save_existing(form, instance, commit=commit)

