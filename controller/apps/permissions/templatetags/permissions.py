from django import template

register = template.Library()

#(not save_as or context['add'])


@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def submit_row(context):
    """
    Displays the row of buttons for delete and save with view permission awearness.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    ctx = {
        'opts': opts,
        'show_delete_link': (not is_popup and context['has_delete_permission']
                              and change and context.get('show_delete', True)),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': (change and context['has_change_permission'] and context['has_add_permission'] ) or 
                       (context['add'] and context['has_add_permission'] and not context['save_and_continue']),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': (change and context['has_change_permission']) or 
                       (context['add'] and context['has_add_permission'] and not context['save_and_continue'])
    }
    if context.get('original') is not None:
        ctx['original'] = context['original']
    return ctx

