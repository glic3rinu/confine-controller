REQUIRED_APPS = ['nodes', 'slices']

from django.db.models.loading import get_model

from controller.utils import plugins


class ResourcePlugin(object):
    name = ''
    unit = ''
    max_req = 0
    dflt_req = 0
    producers = []
    consumers = []
    
    __metaclass__ = plugins.PluginMount
    
    
    def clean(self, resource):
        pass
    
    def clean_req(self, resource):
        pass
    
    def save(self, resource):
        pass
    
    def delete(self, resource):
        pass
    
    def available(self, resource):
        """ Get the number of unused resources. """
        return None
    
    @classmethod
    def get_producers_models(cls):
        return cls._get_related_models('producers')
    
    @classmethod
    def get_consumers_models(cls):
        return cls._get_related_models('consumers')
    
    @classmethod
    def get_resources_for_producer(cls, producer):
        return cls._get_resources_by_type(producer, 'producers')
    
    @classmethod
    def get_resources_for_consumer(cls, consumer):
        return cls._get_resources_by_type(consumer, 'consumers')
    
    @classmethod
    def get(cls, name):
        for resource in cls.plugins:
            if resource.name == name:
                return resource()
        raise KeyError("Resource with name '%s' can not be found" % name)
    
    @classmethod
    def _get_related_models(cls, category):
        models = set()
        for resource in cls.plugins:
            for related in getattr(resource, category):
                if related:
                    models.add(get_model(*related.split('.')))
        return models
    
    @classmethod
    def _get_resources_by_type(cls, model, category):
        resources = []
        opts = model._meta
        model = "%s.%s" % (opts.app_label, opts.object_name)
        for resource in cls.plugins:
            if model in getattr(resource, category):
                resources.append(resource)
        return resources
