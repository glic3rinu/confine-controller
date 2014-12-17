import os, glob

from controller.utils.plugins import PluginMount


class FirmwarePlugin(object):
    description = ''
    verbose_name = ''
    enabled_by_default = False
    
    __metaclass__ = PluginMount
    
    @property
    def form(self):
        self._form = getattr(self, '_form', self.get_form())
        return self._form
    
    @form.setter
    def form(self, value):
        self._form = value
    
    def get_form(self):
        pass
    
    def get_serializer(self):
        pass
    
    def pre_umount(self, image, build, *args, **kwargs):
        pass
    
    def post_umount(self, image, build, *args, **kwargs):
        pass
    
    def build_display(self, build):
        pass
    
    def update_image_name(self, image_name, **kwargs):
        return image_name


modules = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))
for module in modules:
    module_name = os.path.basename(module)[:-3]
    exec 'from firmware.plugins.%s import *' % module_name
