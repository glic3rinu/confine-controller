from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from pings.models import Ping
from pings.admin import STATES_COLORS


register = template.Library()


@register.filter(name='ping_status')
def ping_status(obj):
    ct = ContentType.objects.get_for_model(type(obj))
    state = Ping.get_state(obj)
    context = {
        'color': STATES_COLORS.get(state, "black"),
        'title': state,
        'url': reverse('admin:pings_ping_list', args=(ct.pk, obj.pk)),
        'addr': obj.address
    }
    colored = '<a style="color: %(color)s;" title="%(title)s" href="%(url)s">%(addr)s</a>' % context
    return mark_safe(colored)
