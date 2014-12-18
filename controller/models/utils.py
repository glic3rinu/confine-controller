import os

from django.db import models

from controller.utils.singletons.models import SingletonModel


def generate_chainer_manager(qs_class):
    # Allow chained managers
    # Based on http://djangosnippets.org/snippets/562/#c2486
    class ChainerManager(models.Manager):
        def __init__(self):
            super(ChainerManager,self).__init__()
            self.queryset_class = qs_class
        
        def get_queryset(self):
            return self.queryset_class(self.model)
        
        def __getattr__(self, attr, *args):
            try:
                return getattr(type(self), attr, *args)
            except AttributeError:
                return getattr(self.get_queryset(), attr, *args)
    return ChainerManager()


def get_field_value(obj, field_name):
    names = field_name.split('__')
    rel = getattr(obj, names.pop(0))
    for name in names:
        try:
            rel = getattr(rel, name)
        except AttributeError:
            # maybe it is a query manager
            rel = getattr(rel.get(), name)
    return rel


def get_file_field_base_path(model, field_name):
    """ only works with static upload_to """
    field = model._meta.get_field_by_name(field_name)[0]
    upload_to = field.upload_to
    if callable(upload_to):
        # This is a controller's convention for getting upload_to base path
        upload_to = upload_to(None, '')
    storage_location = field.storage.base_location
    return os.path.join(storage_location, upload_to)


def is_singleton(model):
    return SingletonModel in model.__mro__


def get_help_text(cls, field):
    return cls._meta.get_field_by_name(field)[0].help_text
