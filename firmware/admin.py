from common.admin import get_modeladmin
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.utils.functional import update_wrapper
from firmware.actions import get_firmware
from firmware.models import BaseImage, FirmwareConfig, FirmwareConfigUCI
from nodes.models import Node
from singleton_models.admin import SingletonModelAdmin


class BaseImageInline(admin.TabularInline):
    model = BaseImage
    extra = 0


class FirmwareConfigUCIInline(admin.TabularInline):
    model = FirmwareConfigUCI
    extra = 0



class FirmwareConfigAdmin(SingletonModelAdmin):
    inlines = [BaseImageInline, FirmwareConfigUCIInline]
    
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        
        info = self.model._meta.app_label, self.model._meta.module_name
        
        urlpatterns = patterns('',
            url(r'^history/$', wrap(self.history_view), {'object_id': '1'},
                name='%s_%s_history' % info),
            url(r'^(?P<object_id>\d+)$',
                wrap(self.change_view), 
                name='%s_%s_change' % info),
            url(r'^$',
                wrap(self.change_view), {'object_id': '1'}, 
                name='%s_%s_changelist' % info),
        )
        urls = super(FirmwareConfigAdmin, self).get_urls()
        return urlpatterns + urls


admin.site.register(FirmwareConfig, FirmwareConfigAdmin)


# Monkey-Patching
node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action('firmware', get_firmware, 'Download Firmware', 'viewsitelink')
