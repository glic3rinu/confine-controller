from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.encoding import force_text

from controller.admin.utils import get_admin_link, get_modeladmin

from .exceptions import ConcurrencyError
from .forms import ExecutionForm
from .models import Operation, Instance


@transaction.atomic
def execute_operation_changelist(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.warning(request, "One operation at a time")
        return
    operation = queryset.get()
    return redirect('admin:maintenance_operation_execute', operation.pk)
execute_operation_changelist.short_description = 'Execute operation'


@transaction.atomic
def execute_operation(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    operation = get_object_or_404(Operation, pk=modeladmin.operation_id)
    
    if request.POST.get('post'):
        form = ExecutionForm(request.POST)
        if form.is_valid():
            include_new_nodes = form.cleaned_data['include_new_nodes']
            retry_if_offline = form.cleaned_data['retry_if_offline']
        instances = operation.execute(queryset, include_new_nodes=include_new_nodes,
            retry_if_offline=retry_if_offline)
        for instance in instances:
            msg = 'Executed operation "%s"' % force_text(operation)
            modeladmin.log_change(request, operation, msg)
            instance_modeladmin = get_modeladmin(Instance)
            # AUTO_CREATE instances
            instance_modeladmin.log_addition(request, instance)
            modeladmin.message_user(request, "Successfully created %d instances." % len(instances))
            # Return None to display the change list page again.
            return redirect('admin:maintenance_operation_change', operation.pk)
    
    include_new_nodes = operation.executions.filter(include_new_nodes=True).exists()
    
    context = {
        "title": "Are you sure?",
        "operation": operation,
        "deletable_objects": [[ get_admin_link(node) for node in queryset ]],
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'form': ExecutionForm(initial={'include_new_nodes': include_new_nodes}),
    }
    
    return TemplateResponse(request, "admin/maintenance/operation/execute_operation_confirmation.html",
                            context, current_app=modeladmin.admin_site.name)


@transaction.atomic
def revoke_instance(modeladmin, request, queryset):
    for instance in queryset:
        instance.revoke()
revoke_instance.url_name = 'revoke'
revoke_instance.verbose_name = 'revoke'


@transaction.atomic
def kill_instance(modeladmin, request, queryset):
    for instance in queryset:
        instance.kill()
kill_instance.url_name = 'kill'
kill_instance.verbose_name = 'kill'


@transaction.atomic
def run_instance(modeladmin, request, queryset):
    for instance in queryset:
        try:
            instance.run()
        except ConcurrencyError:
            messages.error(request, "Instance '%s' is alreday running." % instance)
run_instance.url_name = 'run'
run_instance.verbose_name = 'run'


def manage_instances(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.warning(request, "One element at a time")
        return
    obj = queryset.get()
    related_field = 'execution'
    if obj._meta.object_name.lower() == 'operation':
        related_field += '__operation'
    url = reverse('admin:maintenance_instance_changelist')
    url += '?%s=%i' % (related_field, obj.pk)
    return redirect(url)
manage_instances.url = 'mgmt-instances'
manage_instances.verbose_name = 'Manage instances'
