from __future__ import absolute_import

from celery.result import AsyncResult
from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import simplejson
from singleton_models.admin import SingletonModelAdmin

from controller.admin.utils import (get_modeladmin, get_admin_link, insert_action,
    colored, wrap_admin_view)
from nodes.models import Node

from .actions import get_firmware
from .forms import BaseImageFormSet
from .models import (BaseImage, Config, ConfigUCI, Build, ConfigFile,
    ConfigFileHelpText, BuildFile)


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
    formset = BaseImageFormSet


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
    model = BuildFile
    extra = 0
    fields = ['path', 'content']
    readonly_fields = ['path', 'content']
    verbose_name_plural = 'Files'
    can_delete = False
    
    def has_add_permission(self, *args, **kwargs):
        """ Don't show add another link on the inline """
        return False


class ConfigFileInline(admin.TabularInline):
    model = ConfigFile
    extra = 0
    
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


class BuildAdmin(admin.ModelAdmin):
    list_display = ['id', 'node', 'version', colored('state', STATE_COLORS), 
                    'task_link', 'image_link', 'date']
    list_display_links = ['id', 'node']
    search_fields = ['node__description', 'node__id']
    date_hierarchy = 'date'
    list_filter = ['version']
    fields = ['node_link', 'base_image', 'image_link', 'image_sha256', 'version',
              'build_date', 'state', 'task_link', 'task_id']
    readonly_fields = ['node_link', 'state', 'image_link', 'image_sha256',
                       'version', 'build_date', 'task_link', 'task_id', 'base_image']
    inlines = [BuildFileInline]
    
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
        """ Display image url if exsists """
        try:
            return '<a href=%s>%s</a>' % (build.image.url, build.image_name)
        except:
            return ''
    image_link.allow_tags = True
    
    def has_add_permission(self, *args, **kwargs):
        """ Build is a readonly information """
        return False


class ConfigAdmin(SingletonModelAdmin):
    inlines = [BaseImageInline, ConfigUCIInline, ConfigFileInline, ConfigFileHelpTextInline]
    save_on_top = True
    
    def get_urls(self):
        """ Make URLs singleton aware """
        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns = patterns('',
            url(r'^(?P<object_id>\d+)/history/$',
                self.history_view,
                name='%s_%s_history' % info),
            url(r'^(?P<object_id>\d+)/delete/$',
                self.delete_view, 
                name='%s_%s_delete' % info),
            url(r'^(?P<object_id>\d+)$',
                self.change_view, 
                name='%s_%s_change' % info),
            url(r'^$',
                self.change_view, {'object_id': '1'},
                name='%s_%s_changelist' % info),
        )
        urls = super(ConfigAdmin, self).get_urls()
        return urlpatterns + urls
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Warning if the firmware doesn't have any image """
        if request.method == 'GET':
            obj = self.get_object(request, object_id)
            if obj is not None and not obj.images.exists():
                messages.warning(request, "Notice that you don't have any base image configured")
        return super(ConfigAdmin, self).change_view(request, object_id, extra_context=extra_context)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'image_name':
            kwargs['widget'] = forms.TextInput(attrs={'size':'120'})
        return super(ConfigAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def has_delete_permission(self, *args, **kwargs):
        """ It doesn't make sense to delete a singleton configuration """
        return False

admin.site.register(Config, ConfigAdmin)
admin.site.register(Build, BuildAdmin)


# Monkey-Patching Section

insert_action(Node, get_firmware)
node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action(get_firmware)

old_get_urls = node_modeladmin.get_urls

def get_urls(self):
    """ Hook JSON representation of a Build to NodeModeladmin """
    def build_info_view(request, node_id):
        try:
            build = Build.objects.get(node=node_id)
        except Build.DoesNotExist:
            info = {}
        else:
            task = AsyncResult(build.task_id)
            result = task.result or {}
            state = build.state
            if state in [Build.REQUESTED, Build.QUEUED, Build.BUILDING]:
                state = 'PROCESS'
            info = {
                'state': state,
                'progress': result.get('progress', 0),
                'next': result.get('next', 0),
                'description': "%s ..." % result.get('description', 'Waiting for your build task to begin.'),
                'id': build.pk,
                'content_message': build.state_description }
        return HttpResponse(simplejson.dumps(info), mimetype="application/json")
    
    @transaction.commit_on_success
    def delete_build_view(request, node_id):
        node = get_object_or_404(Node, pk=node_id)
        build = get_object_or_404(Build, node=node_id)
        
        # Check that the user has delete permission for the actual model
        node_modeladmin = get_modeladmin(Node)
        if not node_modeladmin.has_change_permission(request, obj=node, view=False):
            raise PermissionDenied
        
        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if request.POST.get('post'):
            build.delete()
            node_modeladmin.log_change(request, node, "Deleted firmware build")
            node_modeladmin.message_user(request, "Firmware build has been successfully deleted.")
            return redirect('admin:nodes_node_firmware', node_id)
        
        context = {
            'opts': node_modeladmin.model._meta,
            'app_label': node_modeladmin.model._meta.app_label,
            'title': 'Are your sure?',
            'build': build,
            'node': node, }
        return render(request, 'admin/firmware/delete_build_confirmation.html', context)
    
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
