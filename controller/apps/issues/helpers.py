from functools import wraps

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.decorators import available_attrs

from controller.admin.utils import admin_link
from issues.models import Message


def log_as_message(modeladmin, ticket, author, info=''):
    """ Generate a message for register the change """
    info = "(%s)" % info if info else ''
    author_link = admin_link('')(author)
    state = modeladmin.colored_state(ticket)
    content = "%s has changed state to %s %s" % (author_link, state, info)
    message = Message(ticket=ticket, author=author, content=content)
    message.save()


#TODO implement using permissions??
def user_has_perm(func):
    """
    Check if the user has the required permission to execute an action
    Inspired in user_passes_test from django.contrib.auth.decorators

    """
    @wraps(func, assigned=available_attrs(func))
    def decorator(modeladmin, request, queryset):
        if request.user.is_superuser:
            return func(modeladmin, request, queryset)
        else:
            msg = "You don't have enought rights to perform this action!"
            modeladmin.message_user(request, msg, messages.ERROR)
            return None #raise PermissionDenied()
    return decorator


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
