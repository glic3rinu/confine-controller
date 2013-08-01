from functools import wraps

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.decorators import available_attrs

from controller.admin.utils import admin_link
from issues.models import Message

# TODO move to controller.utils

def timesince(d, now=None):
    """ Parse django timeago to get only one unit time """
    # Avoid circular imports
    from django.utils.timesince import timesince
    return timesince(d).split(',')[0]


def format_date(d):
    """ 
    Format date for messages create_on: show a relative time
    with contextual helper to show fulltime format.
    """
    date_rel = timesince(d) + ' ago'
    date_abs = d.strftime("%Y-%m-%d %H:%M:%S")
    return "%s <span class='timesince' title='%s'></span>" % (date_rel, date_abs) 


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


def html_formated_changes(changes):
    html = ''
    for name, values in changes.items():
        context = (name.capitalize(), values[0], values[1])
        html += '<li><b>%s</b> changed from %s to %s</li>' % context
    return '<ul>%s</ul>' % html if html else ''


def get_ticket_changes(modeladmin, request, ticket):
    ModelForm = modeladmin.get_form(request, ticket)
    form = ModelForm(request.POST, request.FILES)
    changes = {}
    if form.is_valid():
        # TODO state
        for attr in ['owner', 'visibility', 'priority', 'cc', 'queue']:
            old_value = getattr(ticket, attr)
            new_value = form.cleaned_data[attr]
            if old_value != new_value:
                changes[attr] = (old_value, new_value)
    return changes
