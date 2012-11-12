from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.http import HttpResponse
from django.utils import simplejson
from singleton_models.admin import SingletonModelAdmin

from common.admin import (get_modeladmin, admin_link, insert_action, colored, 
    wrap_admin_view)
from firmware.actions import get_firmware
from firmware.models import BaseImage, Config, ConfigUCI, Build, BuildUCI
from nodes.models import Node


STATE_COLORS = {
    Build.REQUESTED: 'blue',
    Build.QUEUED: 'magenta',
    Build.BUILDING: 'orange',
    Build.AVAILABLE: 'green',
    Build.OUTDATED: 'red',
    Build.DELETED: 'red',
}


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
    list_display = ['id', admin_link('node'), 'version', colored('state', STATE_COLORS), 
                    'task_link', 'image_link', 'date']
    search_fields = ['node__description', 'node__id']
    date_hierarchy = 'date'
    list_filter = ['version']
    fields = ['node_link', 'image_link', 'image_sha256', 'version', 'build_date',
              'state', 'task_link']
    readonly_fields = ['node_link', 'state', 'image_link', 'image_sha256', 
                       'version', 'build_date', 'task_link']
    inlines = [BuildUCIInline]
    
    def build_date(self, build):
        return build.date.strftime("%Y-%m-%d %H:%M:%S")
    
    def node_link(self, build):
        return admin_link('node')(build)
    node_link.short_description = "Node"
    
    def task_link(self, build):
        if build.task:
            return admin_link('')(build.task, href_name=build.task.task_id)
    task_link.allow_tags = True
    task_link.short_description = "Task"
    
    def image_link(self, build):
        try: return '<a href=%s>%s</a>' % (build.image.url, build.image)
        except: return ''
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


# Monkey-Patching Section

insert_action(Node, get_firmware)

node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action('firmware', get_firmware, 'Download Firmware', 'viewsitelink')

old_get_urls = node_modeladmin.get_urls

def get_urls(self):
    """ Hook JSON representation of a Build to NodeModeladmin """
    def build_info(request, node_id):
        try: build = Build.objects.get(node=node_id)
        except Build.DoesNotExist: build_dict = {}
        else: build_dict = {
                'state': build.state,
                'date': build.date.strftime("%Y-%m-%d %H:%M:%S"),
                'image': build.image.name,
                'sha256': build.image_sha256,
                'id': build.pk,
                'version': build.version,}
        return HttpResponse(simplejson.dumps(build_dict), mimetype="application/json")
    
    extra_urls = patterns("", 
        url("^(?P<node_id>\d+)/firmware/build_info/$", 
        wrap_admin_view(self, build_info), 
        name='build_info'),
    )
    return extra_urls + old_get_urls()

type(node_modeladmin).get_urls = get_urls
