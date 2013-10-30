REQUIRED_APPS = ['issues']


from controller.utils import plugins


class ResourcePlugin(object):
    __metaclass__ = plugins.PluginMount

