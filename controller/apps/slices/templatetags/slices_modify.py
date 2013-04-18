from django import template


register = template.Library()


@register.inclusion_tag('admin/slices/slice/list_nodes_actions.html', takes_context=True)
def list_nodes_admin_actions(context):
    """
    Track the number of times the action field has been rendered on the page,
    so we know which value to use.
    """
    context['action_index'] = context.get('action_index', -1) + 1
    return context

