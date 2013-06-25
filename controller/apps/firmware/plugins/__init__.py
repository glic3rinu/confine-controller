import os, glob

from controller.utils.plugins import PluginMount


class FirmwarePlugin(object):
    description = ''
    
    __metaclass__ = PluginMount
    
    def get_form(self, *args, **kwargs):
        pass
    
    def pre_umount(self, image, build, *args, **kwargs):
        pass
    
    def post_umount(self, image, build, *args, **kwargs):
        pass
    
    def build_display(self, build):
        pass


modules = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))
for module in modules:
    module_name = os.path.basename(module)[:-3]
    exec 'from firmware.plugins.%s import *' % module_name
