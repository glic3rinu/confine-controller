from controller.utils.plugins import PluginMount


class Notification(object):
    description = ''
    verbose_name = ''
    
    __metaclass__ = PluginMount
    
    def check_condition(self, obj):
        raise NotImplemented
    
    def get_recipients(self, obj):
        raise NotImplemented
