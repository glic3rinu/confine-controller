from django.apps import AppConfig
from django.contrib.contenttypes import generic

from . import ResourcePlugin


class ResourcesConfig(AppConfig):
    name = 'resources'
    
    def ready(self):
        for producer_model in ResourcePlugin.get_producers_models():
            producer_model.add_to_class('resources', generic.GenericRelation('resources.Resource'))
        
        for consumer_model in ResourcePlugin.get_consumers_models():
            consumer_model.add_to_class('resources', generic.GenericRelation('resources.ResourceReq'))
