from controller.utils import get_controller_site
from controller.utils.plugins import PluginMount


class Notification(object):
    description = ''
    verbose_name = ''
    default_subject = ''
    default_message = ''
    expire_window = None
    
    __metaclass__ = PluginMount
    
    def check_condition(self, obj):
        raise NotImplemented
    
    def get_recipients(self, obj):
        raise NotImplemented
    
    def get_context(self, obj):
        return {
            'site': get_controller_site(),
            'obj': obj }
