from django.db import transaction

from controller.admin.utils import admin_link
from issues.models import Message

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

@transaction.commit_on_success
def log_as_message(modeladmin, ticket, author, info=''):
    """ Generate a message for register the change """
    info = "(%s)" % info if info else ''
    author_link = admin_link('')(author)
    state = modeladmin.colored_state(ticket)
    content = "%s has changed state to %s %s" % (author_link, state, info)
    message = Message(ticket=ticket, author=author, content=content)
    message.save()

