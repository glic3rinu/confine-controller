from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter

from controller.admin import ChangeViewActions
from controller.admin.utils import get_admin_link, colored, admin_link, wrap_admin_view
from nodes.admin import NodeAdmin
from nodes.models import Node
from permissions.admin import PermissionModelAdmin

from .actions import ( execute_operation, execute_operation_changelist, run_instance,
    revoke_instance )
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
    Execution.COMPLETE: 'green'}


def num_instances(instance):
    total = instance.instances.count()
    done = instance.instances.exclude(state__in=[Instance.TIMEOUT,
        Instance.RECEIVED, Instance.STARTED]).count()
    url = reverse('admin:maintenance_instance_changelist')
    url += '?%s=%s' % (instance._meta.module_name, instance.pk)
    return mark_safe('<b><a href="%s">%d out of %d</a></b>' % (url, done, total))
num_instances.short_description = 'Instances'


def colored_state(instance):
    color = colored('state', STATE_COLORS)
    return mark_safe(color(instance))
colored_state.short_description = 'State'


class ExecutionInline(admin.TabularInline):
    model = Execution
    fields = [num_instances, 'is_active', 'include_new_nodes', 'created_on', 
              'details', colored_state]
    readonly_fields = ['created_on', num_instances, colored_state, 'details']
    extra = 0
    form = ExecutionInlineForm
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def details(self, instance):
        return mark_safe("<b>%s</b>" % get_admin_link(instance, href_name='details'))


class InstanceInline(admin.TabularInline):
    model = Instance
    extra = 0
    fields = ['node_link', colored_state, 'last_try', 'details', 'exit_code']
    readonly_fields = ['node_link', colored_state, 'last_try', 'details', 'exit_code']
    
    def node_link(self, instance):
        """ Link to related node used on change_view """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.node))
    node_link.short_description = 'Node'
    
    def details(self, instance):
        return mark_safe("<b>%s</b>" % get_admin_link(instance, href_name='details'))


class NodeListAdmin(NodeAdmin):
    """ 
    Nested Node ModelAdmin that provides a list of available nodes for adding 
    slivers hooked on Operation
    """
    # Template that fixes breadcrumbs for the new namespace
    change_list_template = 'admin/maintenance/operation/list_nodes.html'
    actions = [execute_operation]
    actions_on_bottom = True
    
    def get_actions(self, request):
        """ Avoid inherit NodeAdmin actions """
        actions = super(NodeListAdmin, self).get_actions(request)
        return {'execute_operation': actions['execute_operation']}
    
    def changelist_view(self, request, operation_id, extra_context=None):
        """ Just fixing title and breadcrumbs """
        self.operation_id = operation_id
        operation = Operation.objects.get(pk=operation_id)
        title = 'Select one or more nodes for executing %s operation' % get_admin_link(operation)
        context = {'title': mark_safe(title),
                   'operation': operation, }
        context.update(extra_context or {})
        # call admin.ModelAdmin to avoid my_nodes default NodeAdmin changelist filter
        return admin.ModelAdmin.changelist_view(self, request, extra_context=context)
    
    def has_add_permission(self, *args, **kwargs):
        """ Prevent node addition on this ModelAdmin """
        return False


class OperationAdmin(PermissionModelAdmin):
    list_display = ['name', 'identifier', 'num_executions', 'has_active_executions',
                    'has_include_new_nodes', 'num_instances']
    list_display_links = ['name', 'identifier']
    list_filter = ['executions__is_active']
    inlines = [ExecutionInline]
    actions = [execute_operation_changelist]
    save_and_continue = True
    # TODO fix this annoying mandatory declaration once and for all
    change_form_template = "admin/maintenance/operation/change_form.html"
    
    def num_executions(self, instance):
        num = instance.executions.count()
        url = reverse('admin:maintenance_execution_changelist')
        url += '?%s=%s' % (instance._meta.module_name, instance.pk)
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
        opts = self.model._meta
        extra_urls = patterns("",
            url("^(?P<operation_id>\d+)/execute/$",
                wrap_admin_view(self, NodeListAdmin(Node, admin_site).changelist_view),
                name='maintenance_operation_execute'),
        )
        return extra_urls + urls


class ExecutionAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', admin_link('operation'), 'is_active',
                    'include_new_nodes', num_instances]
    inlines = [InstanceInline]
    readonly_fields = ['operation_link', 'display_script']
    list_filter = ['is_active', 'include_new_nodes']
    fields = ['operation_link', 'display_script', 'is_active', 'include_new_nodes']
    
    class Media:
        css = { "all": ("controller/css/github.css", "state/admin/css/details.css") }
    
    def display_script(self, instance):
        style = ('<style>code,pre {font-size:1.13em;}</style>'
                 '<div style="padding-left:100px;">')
        return mark_safe(style + highlight(instance.script, BashLexer(), HtmlFormatter()))
    display_script.short_description = 'script'
    
    def operation_link(self, instance):
        return mark_safe("<b>%s</b>" % get_admin_link(instance.operation))
    operation_link.short_description = 'operation'


class InstanceAdmin(ChangeViewActions):
    list_display = ['__unicode__', admin_link('execution__operation'), admin_link('execution'),
                    admin_link('node'), colored('state', STATE_COLORS), 'last_try']
    list_filter = ['state', 'execution__operation__identifier', 'execution__is_active']
    readonly_fields = ['execution', 'node', 'last_try', 'stdout', 'stderr',
                       'exit_code', 'traceback', 'state']
    actions = [revoke_instance, run_instance]
    change_view_actions = [revoke_instance, run_instance]
    
    def lookup_allowed(self, key, value):
        if key == 'execution__operation':
            return True
        return super(InstanceAdmin, self).lookup_allowed(key, value)


admin.site.register(Operation, OperationAdmin)
admin.site.register(Execution, ExecutionAdmin)
admin.site.register(Instance, InstanceAdmin)
