from controller.admin.utils import get_admin_link

def filter_actions(modeladmin, ticket, request):
    if not hasattr(modeladmin, 'change_view_actions_backup'):
        modeladmin.change_view_actions_backup = list(modeladmin.change_view_actions)
    actions = modeladmin.change_view_actions_backup
    if ticket.state == modeladmin.model.CLOSED:
        del_actions = actions
    else:
        from issues.actions import action_map
        del_actions = [action_map.get(ticket.state, None)]
        if ticket.owner == request.user:
            del_actions.append('take')
    exclude = lambda a: not (a == action or a.url_name == action)
    for action in del_actions:
        actions = filter(exclude, actions)
    return actions


def markdown_formated_changes(changes):
    markdown = ''
    for name, values in changes.items():
        context = (name.capitalize(), values[0], values[1])
        markdown += '* **%s** changed from _%s_ to _%s_\n' % context
    return markdown + '\n'


def get_ticket_changes(modeladmin, request, ticket):
    ModelForm = modeladmin.get_form(request, ticket)
    form = ModelForm(request.POST, request.FILES)
    changes = {}
    if form.is_valid():
        for attr in ['state', 'visibility', 'priority', 'group', 'owner', 'queue']:
            old_value = getattr(ticket, attr)
            new_value = form.cleaned_data[attr]
            if old_value != new_value:
                changes[attr] = (old_value, new_value)
    return changes


def display_author(obj, field_name, href_name=''):
    """Get link or stored name if user doesn't exists (#289)"""
    author = getattr(obj, field_name)
    if author is None:
        return '<span class="author">%s</span>' % getattr(obj, field_name + '_name')
    return get_admin_link(author)
