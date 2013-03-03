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
