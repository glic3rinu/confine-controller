from django.db import models


def generate_chainer_manager(qs_class):
    # Allow chained managers
    # Based on http://djangosnippets.org/snippets/562/#c2486
    class ChainerManager(models.Manager):
        def __init__(self):
            super(ChainerManager,self).__init__()
            self.queryset_class = qs_class

        def get_query_set(self):
            return self.queryset_class(self.model)

        def __getattr__(self, attr, *args):
            try:
                return getattr(type(self), attr, *args)
            except AttributeError:
                return getattr(self.get_query_set(), attr, *args)
    return ChainerManager()


## Add South introspect rules for private_files.PrivateField
from django.conf import settings
if 'private_files' and 'south' in settings.INSTALLED_APPS:
    from private_files import PrivateFileField
    from south.modelsinspector import add_introspection_rules
    rules = [((PrivateFileField,), [], {"attachment" : ["attachment", {"default": True}],},)]
    add_introspection_rules(rules, ["^private_files\.models\.fields\.PrivateFileField"])

