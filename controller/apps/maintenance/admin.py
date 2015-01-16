from __future__ import absolute_import

from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter

from controller.admin import ChangeViewActions
from controller.admin.utils import (get_admin_link, colored, admin_link, wrap_admin_view,
    action_to_view, display_timesince)
from controller.utils.html import monospace_format, MONOSPACE_FONTS
from nodes.admin import NodeAdmin
from nodes.models import Node
from permissions.admin import PermissionModelAdmin

from .actions import ( execute_operation, run_instance, kill_instance,
    revoke_instance, manage_instances )
from .forms import ExecutionInlineForm
from .models import Operation, Execution, Instance


STATE_COLORS = {
    Instance.RECEIVED: 'blue',
    Instance.TIMEOUT: 'darkorange',
    Instance.STARTED: 'yellow',
    Instance.SUCCESS: 'green',
    Instance.FAILURE: 'red',
    Instance.REVOKED: 'purple',
    Instance.OUTDATED: 'dark',
    Execution.PROGRESS: 'blue',
    Execution.COMPLETE: 'green'
}


def num_instances(execution):
    total = execution.instances.count()
    final_states = [Instance.RECEIVED, Instance.STARTED]
    done = execution.instances.exclude(state__in=final_states)
    if execution.retry_if_offline:
        done = done.exclude(state=Instance.TIMEOUT)
    done = done.count()
    url = reverse('admin:maintenance_instance_changelist')
    url += '?%s=%s' % (execution._meta.model_name, execution.pk)
    return mark_safe('<b><a href="%s">%d out of %d</a></b>' % (url, done, total))
num_instances.short_description = 'Instances'


def colored_state(instance):
    color = colored('state', STATE_COLORS)
    return mark_safe(color(instance))
colored_state.short_description = 'State'


def state_link(instance):
    state = colored_state(instance)
    return mark_safe("<b>%s</b>" % get_admin_link(instance, href_name=state))
state_link.short_description = 'State'
state_link.admin_order_field = 'state'


def last_try(instance):
    return display_timesince(instance.last_try)
last_try.admin_order_field = 'last_try'


class ExecutionInline(admin.TabularInline):
    fields = [
        'execution_link', num_instances, 'is_active', 'include_new_nodes',
        'retry_if_offline', 'created', 'state'
    ]
    model = Execution
    readonly_fields = ['execution_link', 'created', num_instances, 'state']
    extra = 0
    form = ExecutionInlineForm
    
    def execution_link(self, execution):
        return mark_safe('<b>' + get_admin_link(execution) + '</b>')
    execution_link.short_description = '#'
    
    def created(self, execution):
        return display_timesince(execution.created_on)
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def state(self, instance):
        state = colored_state(instance)
        return mark_safe("<b>%s</b>" % get_admin_link(instance, href_name=state)) 


class InstanceInline(admin.TabularInline):
    model = Instance
    extra = 0
    max_num = 0
    fields = ['node_link', state_link, last_try, 'exit_code']
    readonly_fields = ['node_link', state_link, last_try, 'exit_code']
    
    def node_link(self, instance):
        """ Link to related node used on change_view """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.node))
    node_link.short_description = 'Node'
    
    def has_add_permission(self, *args, **kwargs):
        return False


class NodeListAdmin(NodeAdmin):
    """ 
    Nested Node ModelAdmin that provides a list of available nodes for adding 
    slivers hooked on Operation
    """
    # Template that fixes breadcrumbs for the new namespace
    list_display = ['execute_node'] + NodeAdmin.list_display[1:]
    list_display_links = ['execute_node', 'id']
    change_list_template = 'admin/maintenance/operation/list_nodes.html'
    actions = [execute_operation]
    change_list_actions = [execute_operation]
    actions_on_bottom = True
    
    def execute_node(self, instance):
        args = [self.operation_id, instance.pk]
        url = reverse('admin:maintenance_operation_execute_node', args=args)
        return mark_safe('<a href="%s">%s</a>' % (url, instance))
    execute_node.short_description = 'Node'
    
    def get_actions(self, request):
        """ Avoid inherit NodeAdmin actions """
        actions = super(NodeListAdmin, self).get_actions(request)
        return {'execute_operation': actions['execute_operation']}
    
    def changelist_view(self, request, operation_id, extra_context=None):
        """ Just fixing title and breadcrumbs """
        operation = get_object_or_404(Operation, pk=operation_id)
        self.operation_id = operation_id
        link = get_admin_link(operation)
        title = 'Select one or more nodes for executing %s operation' % link
        context = {
            'title': mark_safe(title),
            'header_title': 'Executing %s operation' % operation,
            'operation': operation
        }
        context.update(extra_context or {})
        # call admin.ModelAdmin to avoid my_nodes default NodeAdmin changelist filter
        return admin.ModelAdmin.changelist_view(self, request, extra_context=context)
    
    def execute_operation_view(self, request, operation_id, node_id):
        self.operation_id = operation_id
        _execute_operation_view = action_to_view(execute_operation, self)
        return _execute_operation_view(request, node_id)
    
    def has_add_permission(self, *args, **kwargs):
        """ Prevent node addition on this ModelAdmin """
        return False


class OperationAdmin(PermissionModelAdmin, ChangeViewActions):
    list_display = [
        'name', 'identifier', 'num_executions', 'has_active_executions',
        'has_include_new_nodes', 'num_instances'
    ]
    list_display_links = ['name', 'identifier']
    list_filter = ['executions__is_active']
    inlines = [ExecutionInline]
    save_and_continue = True
    actions = [manage_instances]
    change_view_actions = [manage_instances]
    # TODO fix this annoying mandatory declaration once and for all
    change_form_template = "admin/maintenance/operation/change_form.html"
    
    class Media:
        css = { 'all': ('controller/css/hide-inline-id.css',) }
    
    def num_executions(self, instance):
        num = instance.executions.count()
        url = reverse('admin:maintenance_execution_changelist')
        url += '?%s=%s' % (instance._meta.model_name, instance.pk)
        return mark_safe('<a href="%s">%d</a>' % (url, num))
    num_executions.short_description = 'Executions'
    
    def has_active_executions(self, instance):
        return instance.executions.filter(is_active=True).exists()
    has_active_executions.short_description = 'is active'
    has_active_executions.boolean = True
    
    def has_include_new_nodes(self, instance):
        return instance.executions.filter(include_new_nodes=True).exists()
    has_include_new_nodes.short_description = 'include new nodes'
    has_include_new_nodes.boolean = True
    
    def num_instances(self, instance):
        base_instances = Instance.objects.filter(execution__operation=instance,
            execution__is_active=True)
        total = base_instances.count()
        done = base_instances.exclude(state__in=[Instance.TIMEOUT, Instance.RECEIVED,
            Instance.STARTED]).count()
        url = reverse('admin:maintenance_instance_changelist')
        url += '?execution__operation=%s' % instance.pk
        return mark_safe('<b><a href="%s">%d out of %d</a></b>' % (url, done, total))
    num_instances.short_description = 'instances'
    
    def get_urls(self):
        urls = super(OperationAdmin, self).get_urls()
        admin_site = self.admin_site
        extra_urls = patterns("",
            url("^(?P<operation_id>\d+)/execute/$",
                wrap_admin_view(self, NodeListAdmin(Node, admin_site).changelist_view),
                name='maintenance_operation_execute'),
            url("^(?P<operation_id>\d+)/execute/(?P<node_id>\d+)/$",
                wrap_admin_view(self, NodeListAdmin(Node, admin_site).execute_operation_view),
                name='maintenance_operation_execute_node'),
        )
        return extra_urls + urls
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Use monospace font style in script textarea """
        if db_field.name == 'script':
            kwargs['widget'] = forms.Textarea(
                attrs={'cols': 85, 'rows': '10', 'style': 'font-family:%s' % MONOSPACE_FONTS })
        return super(OperationAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class ExecutionAdmin(ChangeViewActions):
    list_display = [
        '__unicode__', admin_link('operation'), 'is_active', 'include_new_nodes',
        'retry_if_offline', num_instances
    ]
    list_filter = ['is_active', 'include_new_nodes', 'retry_if_offline', 'operation']
    inlines = [InstanceInline]
    readonly_fields = ['operation_link', 'display_script']
    fields = [
        'operation_link', 'display_script', 'is_active', 'include_new_nodes',
        'retry_if_offline'
    ]
    change_view_actions = [manage_instances]
    
    class Media:
        css = {
            "all": (
                "controller/css/github.css",
                "state/admin/css/details.css",
                "controller/css/hide-inline-id.css")
        }
    
    def display_script(self, instance):
        style = ('<style>code,pre {font-size:1.13em;}</style>'
                 '<div style="padding-left:100px;">')
        script = highlight(instance.script, BashLexer(), HtmlFormatter())
        return mark_safe(style + script)
    display_script.short_description = 'script'
    
    def operation_link(self, instance):
        return mark_safe("<b>%s</b>" % get_admin_link(instance.operation))
    operation_link.short_description = 'operation'

    def has_add_permission(self, request):
        """ Avoid add execution directly, must be added via an operation """
        return False
    
    def get_queryset(self, request):
        related = ('operation',)
        return super(ExecutionAdmin, self).get_queryset(request).select_related(*related)


class InstanceAdmin(ChangeViewActions):
    list_display = [
        '__unicode__', 'display_operation', 'display_execution', 'node_link',
        state_link, last_try, 'execution__retry_if_offline'
    ]
    list_filter = [
        'state', 'execution__operation__identifier', 'execution__is_active',
        'execution__retry_if_offline'
    ]
    fields = [
        'display_operation', 'display_execution', 'node_link', last_try, 'mono_stdout',
        'mono_stderr', 'exit_code', 'traceback', 'state', 'task_link'
    ]
    readonly_fields = [
        'display_operation', 'display_execution', 'node_link', last_try, 'mono_stdout',
        'mono_stderr', 'exit_code', 'traceback', 'state', 'task_link'
    ]
    actions = [kill_instance, revoke_instance, run_instance]
    change_view_actions = [kill_instance, revoke_instance, run_instance]
    change_form_template = 'admin/maintenance/instance/change_form.html'
    
    def execution__retry_if_offline(self, instance):
        return instance.execution.retry_if_offline
    execution__retry_if_offline.short_description = 'retry if offline'
    execution__retry_if_offline.boolean = True
    
    def node_link(self, instance):
        return get_admin_link(instance.node)
    node_link.short_description = 'Node'
    
    def task_link(self, build):
        """ Display Celery task change view if exists """
        if build.db_task:
            return get_admin_link(build.db_task, href_name=build.db_task.task_id)
    task_link.allow_tags = True
    task_link.short_description = "Task"
    
    def display_operation(self, instance):
        return get_admin_link(instance.execution.operation)
    display_operation.short_description = 'Operation'
    display_operation.admin_order_field = 'execution__operation'
    
    def display_execution(self, instance):
        return get_admin_link(instance.execution)
    display_execution.short_description = 'execution'
    display_execution.admin_order_field = 'execution'
    
    def lookup_allowed(self, key, value):
        if key == 'execution__operation':
            return True
        return super(InstanceAdmin, self).lookup_allowed(key, value)
    
    def mono_stdout(self, instance):
        return monospace_format(instance.stdout)
    mono_stdout.short_description = 'stdout'
    
    def mono_stderr(self, instance):
        return monospace_format(instance.stderr)
    mono_stderr.short_description = 'stderr'
    
    def changelist_view(self, request, extra_context=None):
        context = {}
        for query, model in [('execution__operation', Operation), ('execution', Execution)]:
            pk = request.GET.get(query, False)
            if pk:
                related_object = model.objects.get(pk=pk)
                url = get_admin_link(related_object)
                name = related_object._meta.object_name.lower()
                changelist_url = reverse('admin:maintenance_%s_changelist' % name)
                changelist_url = '<a href="%s">%s</a>' % (changelist_url, name.capitalize())
                context = {
                    'title': mark_safe('Manage instances of %s %s' % (name, url)),
                    'related_object_url': url,
                    'related_object_changelist_url': mark_safe(changelist_url)
                }
                break
        context.update(extra_context or {})
        return super(InstanceAdmin, self).changelist_view(request, extra_context=context)
    
    def get_queryset(self, request):
        related = ('execution', 'node')
        return super(InstanceAdmin, self).get_queryset(request).select_related(*related)


admin.site.register(Operation, OperationAdmin)
admin.site.register(Execution, ExecutionAdmin)
admin.site.register(Instance, InstanceAdmin)
