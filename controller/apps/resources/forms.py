from django import forms
from django.contrib.contenttypes import generic

from . import ResourcePlugin
from .models import Resource


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
                prefix+'MAX_NUM_FORMS': u'',
            }
            for num, resource in enumerate(resources):
                initial_data[prefix+'%d-name' % num] = resource.name
                initial_data[prefix+'%d-max_sliver' % num] = resource.max_sliver
                initial_data[prefix+'%d-dflt_sliver' % num] = resource.dflt_sliver
            kwargs['data'] = initial_data
        super(ResourceInlineFormSet, self).__init__(*args, **kwargs)
