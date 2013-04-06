from django.db import transaction


@transaction.commit_on_success
def execute_operation(modeladmin, request, queryset):
    from nodes.models import Node
    nodes = Node.objects.all()
    for operation in queryset:
        operation.execute(nodes)
execute_operation.url_name = 'execute'
execute_operation.verbose_name = 'Execute'
