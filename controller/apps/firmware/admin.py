from __future__ import absolute_import

from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from controller.admin import ChangeViewActions
from controller.admin.utils import (get_modeladmin, get_admin_link, insertattr,
    colored, wrap_admin_view, docstring_as_help_tip)
from controller.utils.html import monospace_format
from controller.utils.singletons.admin import SingletonModelAdmin
from nodes.models import Node
from permissions.admin import PermissionTabularInline

from .actions import get_firmware, sync_plugins
from .models import (BaseImage, Config, ConfigUCI, Build, ConfigFile, ConfigPlugin,
    ConfigFileHelpText, BuildFile, NodeBuildFile)
from .views import build_info_view, delete_build_view


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
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'value':
            kwargs['widget'] = forms.TextInput(attrs={'size':'100'})
        return super(ConfigUCIInline, self).formfield_for_dbfield(db_field, **kwargs)


class BuildFileInline(admin.TabularInline):
    """ Readonly inline for displaying build files """
    fields = ['path', 'monospace_content']
    readonly_fields = ['path', 'monospace_content']
    model = BuildFile
    extra = 0
    verbose_name_plural = 'Files'
    can_delete = False
    
    def has_add_permission(self, *args, **kwargs):
        """ Don't show add another link on the inline """
        return False
    
    def monospace_content(self, instance):
        return monospace_format(instance.content)
    monospace_content.short_description = 'Content'


class ConfigFileInline(admin.TabularInline):
    model = ConfigFile
    extra = 0
    ordering = ['-priority', 'path']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make some char input widgets larger """
        if db_field.name == 'path':
            kwargs['widget'] = forms.TextInput(attrs={'size':'60'})
        if db_field.name == 'content':
            kwargs['widget'] = forms.TextInput(attrs={'size':'85'})
        if db_field.name == 'mode':
            kwargs['widget'] = forms.TextInput(attrs={'size':'4'})
        if db_field.name == 'priority':
            kwargs['widget'] = forms.TextInput(attrs={'size':'2'})
        return super(ConfigFileInline, self).formfield_for_dbfield(db_field, **kwargs)


class ConfigFileHelpTextInline(admin.TabularInline):
    model = ConfigFileHelpText
    extra = 0
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'help_text':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 5})
        return super(ConfigFileHelpTextInline, self).formfield_for_dbfield(db_field, **kwargs)


class ConfigPluginInline(admin.TabularInline):
    model = ConfigPlugin
    extra = 0
    readonly_fields = ('label', 'module', 'description')
    
    def description(self, plugin):
        return plugin.instance.description
    
    def has_add_permission(self, *args, **kwargs):
        """ Don't show add another link on the inline """
        return False


class BuildAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'node', 'version', 'colored_state', 'task_link',
        'image_link', 'date'
    ]
    list_display_links = ['pk', 'node']
    search_fields = ['node__description', 'node__id', 'node__name']
    date_hierarchy = 'date'
    list_filter = ['version']
    fields = [
        'node_link', 'base_image', 'image_link', 'image_sha256', 'version',
        'build_date', 'state', 'task_link', 'task_id', 'kwargs'
    ]
    readonly_fields = [
        'node_link', 'state', 'image_link', 'image_sha256', 'kwargs', 'version',
        'build_date', 'task_link', 'task_id', 'base_image'
    ]
    inlines = [BuildFileInline]
    
    class Media:
        css = {
             'all': ('firmware/css/firmware-build.css',)
        }
    
    def colored_state(self, build):
        return colored('state', STATE_COLORS)(build)
    colored_state.short_description = "State"
    
    def build_date(self, build):
        return build.date.strftime("%Y-%m-%d %H:%M:%S")
    
    def node_link(self, build):
        return get_admin_link(build.node)
    node_link.short_description = "Node"
    
    def task_link(self, build):
        """ Display Celery task change view if exists """
        if build.db_task:
            return get_admin_link(build.db_task, href_name=build.db_task.task_id)
    task_link.allow_tags = True
    task_link.short_description = "Task"
    
    def image_link(self, build):
        """ Display image url if exists """
        try:
            return '<a href=%s>%s</a>' % (build.image.url, build.image_name)
        except:
            return ''
    image_link.allow_tags = True
    
    def has_add_permission(self, *args, **kwargs):
        """ Build is a readonly information """
        return False


class ConfigAdmin(ChangeViewActions, SingletonModelAdmin):
    inlines = [
        BaseImageInline, ConfigUCIInline, ConfigFileInline, ConfigFileHelpTextInline,
        ConfigPluginInline
    ]
    change_view_actions = [sync_plugins]
    change_form_template = "admin/controller/change_form.html"
    save_on_top = True
    
    class Media:
        css = {
             'all': (
                'controller/css/hide-inline-id.css',)
        }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'image_name':
            kwargs['widget'] = forms.TextInput(attrs={'size':'120'})
        return super(ConfigAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def has_delete_permission(self, *args, **kwargs):
        """ It doesn't make sense to delete a singleton configuration """
        return False
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Warning if the firmware doesn't have any image """
        if request.method == 'GET':
            obj = self.get_object(request, object_id)
            if obj is not None and not obj.images.exists():
                msg = "Notice that you don't have any base image configured"
                messages.warning(request, msg)
        return super(ConfigAdmin, self).change_view(request, object_id,
                extra_context=extra_context)


class NodeBuildFileInline(PermissionTabularInline):
    """
    Provide a form to retrieve or provide node private keys
    allowing keeping them between firmware generations.
    """
    model = NodeBuildFile
    extra = 0
    fields = ('path', 'content')
    readonly_fields = ('path',)
    verbose_name = 'node key'
    verbose_name_plural = mark_safe('node keys %s' % docstring_as_help_tip(NodeBuildFile))

    class Media:
        js = ('firmware/collapsed_nodekeys.js',)
    
    def has_add_permission(self, request):
        return False
    
    def get_queryset(self, request):
        """
        Hide objects when user has no enought rights.
        Only superusers or node admins can view sensible data.
        """
        qs = super(NodeBuildFileInline, self).get_queryset(request)
        node = qs.first().node if qs.first() else None
        if (request.user.is_superuser or node and
            node.group.has_roles(request.user, roles=['group_admin', 'node_admin'])):
            return qs
        return qs.none()



admin.site.register(Config, ConfigAdmin)
admin.site.register(Build, BuildAdmin)


# Monkey-Patching Section

insertattr(Node, 'inlines', NodeBuildFileInline, weight=4)
insertattr(Node, 'actions', get_firmware)
node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action(get_firmware)

old_get_urls = node_modeladmin.get_urls
def get_urls(self):
    extra_urls = patterns("", 
        url("^(?P<node_id>\d+)/firmware/info/$",
            wrap_admin_view(self, build_info_view),
            name='nodes_node_firmware_build_info'),
        url("^(?P<node_id>\d+)/firmware/delete/$",
            wrap_admin_view(self, delete_build_view),
            name='nodes_node_firmware_delete'),
    )
    return extra_urls + old_get_urls()

type(node_modeladmin).get_urls = get_urls
