from common.admin import get_modeladmin, admin_link, insert_action
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.utils.safestring import mark_safe
from firmware.actions import get_firmware
from firmware.models import BaseImage, Config, ConfigUCI, Build, BuildUCI
from nodes.models import Node
from singleton_models.admin import SingletonModelAdmin


class BaseImageInline(admin.TabularInline):
    model = BaseImage
    extra = 0


class ConfigUCIInline(admin.TabularInline):
    model = ConfigUCI
    extra = 0


class BuildUCIInline(admin.TabularInline):
    model = BuildUCI
    max_num = 0
    readonly_fields = ['section', 'option', 'value']
    can_delete = False


class BuildAdmin(admin.ModelAdmin):
    list_display = ['node', 'version', 'build_date', 'image_link']
    fields = ['node_link', 'image_link', 'version', 'build_date']
    inlines = [BuildUCIInline]
    readonly_fields = ['node_link', 'image_link', 'version', 'build_date']
    
    def build_date(self, build):
        return build.date.strftime("%Y-%m-%d %H:%M:%S")
    
    def node_link(self, build):
        return mark_safe(admin_link('node')(build))
    node_link.short_description = "Node"
    
    def image_link(self, build):
        return mark_safe('<a href=%s>%s</a>' % (build.image.url, build.image))
    image_link.allow_tags = True
    
    def has_add_permission(self, *args, **kwargs):
        return False


class ConfigAdmin(SingletonModelAdmin):
    inlines = [BaseImageInline, ConfigUCIInline]
    
    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns = patterns('',
            url(r'^history/$', 
                self.history_view, {'object_id': '1'},
                name='%s_%s_history' % info),
            url(r'^(?P<object_id>\d+)$',
                self.change_view, 
                name='%s_%s_change' % info),
            url(r'^$',
                self.change_view, {'object_id': '1'}, 
                name='%s_%s_changelist' % info),
        )
        urls = super(ConfigAdmin, self).get_urls()
        return urlpatterns + urls


admin.site.register(Config, ConfigAdmin)
admin.site.register(Build, BuildAdmin)


# Monkey-Patching
insert_action(Node, get_firmware)

node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action('firmware', get_firmware, 'Download Firmware', 'viewsitelink')
