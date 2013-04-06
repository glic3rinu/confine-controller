from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from controller.admin import ChangeViewActions
from controller.admin.utils import get_admin_link, colored, admin_link

from .actions import execute_operation
from .models import Operation, Execution, Instance


STATE_COLORS = {
    Instance.RECEIVED: 'blue',
    Instance.TIMEOUT: 'darkorange',
    Instance.STARTED: 'yellow',
    Instance.SUCCESS: 'green',
    Instance.FAILURE: 'red',
    Instance.REVOKED: 'purple'}


def num_instances(instance):
    num = instance.instances.count()
    url = reverse('admin:maintenance_instance_changelist')
    url += '?%s=%s' % (instance._meta.module_name, instance.pk)
    return mark_safe('<a href="%s">%d</a>' % (url, num))
num_instances.short_description = 'Instances'


def finished(instance):
    fin = instance.instances.exclude(state=Instance.TIMEOUT).count()
    total = instance.instances.count()
    return "%d/%d" % (fin, total)


class ExecutionInline(admin.TabularInline):
    # TODO older as readonly
    model = Execution
    fields = [num_instances, 'is_active', 'include_new_nodes', 'created_on',
              finished]
    readonly_fields = ['created_on', num_instances, finished]
    extra = 0
    can_delete = False
    
    def has_add_permission(self, *args, **kwargs):
        return False


class InstanceInline(admin.TabularInline):
    model = Instance
    extra = 0
    fields = ['node_link', 'colored_state', 'last_try', 'stdout', 'stderr', 'exit_code']
    readonly_fields = ['node_link', 'colored_state', 'last_try', 'stdout',
                       'stderr', 'exit_code']
    
    def node_link(self, instance):
        """ Link to related node used on change_view """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.node))
    node_link.short_description = 'Node'
    
    def colored_state(self, instance):
        color = colored('state', STATE_COLORS, verbose=True)
        return mark_safe(color(instance))


class OperationAdmin(ChangeViewActions):
    list_display = ['name', 'identifier', 'num_executions']
    list_link = ['name', 'identifier']
    inlines = [ExecutionInline]
    actions = [execute_operation]
    change_view_actions = [execute_operation]

    def num_executions(self, instance):
        num = instance.executions.count()
        url = reverse('admin:maintenance_execution_changelist')
        url += '?%s=%s' % (instance._meta.module_name, instance.pk)
        return mark_safe('<a href="%s">%d</a>' % (url, num))
    num_executions.short_description = 'Executions'


class ExecutionAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', admin_link('operation'), 'is_active',
                    'include_new_nodes', num_instances, finished]
    inlines = [InstanceInline]
    readonly_fields = ['operation', 'script']
    list_filter = ['is_active', 'include_new_nodes']


class InstanceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', admin_link('execution__operation'), admin_link('execution'),
                    admin_link('node'), colored('state', STATE_COLORS, verbose=True),
                    'last_try']
    list_filter = ['state']
    readonly_fields = ['execution', 'node', 'last_try', 'stdout', 'stderr',
                       'exit_code', 'traceback',]


admin.site.register(Operation, OperationAdmin)
admin.site.register(Execution, ExecutionAdmin)
admin.site.register(Instance, InstanceAdmin)


