from django.utils.importlib import import_module

from . import settings


def get_mgmt_backend(obj):
    mod, inst = settings.NODES_MGMT_BACKEND.rsplit('.', 1)
    mod = import_module(mod)
    return getattr(mod, inst)(obj)
