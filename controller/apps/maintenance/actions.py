from django.db import transaction


@transaction.commit_on_success
def execute_operation(modeladmin, request, queryset):
    from nodes.models import Node
    nodes = Node.objects.all()
    for operation in queryset:
        operation.execute(nodes)
execute_operation.url_name = 'execute'
execute_operation.verbose_name = 'execute'


@transaction.commit_on_success
def revoke_instance(modeladmin, request, queryset):
    for instance in queryset:
        instance.revoke()
revoke_instance.url_name = 'revoke'
revoke_instance.verbose_name = 'revoke'


@transaction.commit_on_success
def run_instance(modeladmin, request, queryset):
    for instance in queryset:
        instance.run()
run_instance.url_name = 'run'
run_instance.verbose_name = 'run'

