from __future__ import absolute_import

import datetime
import json

from django.contrib import admin
from django.contrib.admin.util import unquote
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from controller.admin import ChangeViewActions
from controller.admin.utils import (insertattr, get_admin_link, colored, get_modeladmin,
        wrap_admin_view, display_timesince, display_timeuntil)
from controller.models.utils import get_help_text
from controller.utils.html import urlize
from controller.utils.time import timesince
from nodes.admin import STATES_COLORS as NODE_STATES_COLORS
from nodes.models import Node
from permissions.admin import PermissionModelAdmin
from slices.admin import (SliverInline, SliverNodeInline, NodeListAdmin, SliceAdmin,
        SliceSliversAdmin)
from slices.admin import STATE_COLORS as SLIVER_STATES_COLORS
from slices.helpers import wrap_action
from slices.models import Sliver, Slice

from .actions import refresh, refresh_state, show_state
from .filters import (NodeStateListFilter, SliverStateListFilter,
    StateContentTypeFilter, FirmwareVersionListFilter)
from .helpers import (break_headers, break_lines, extract_disk_available,
    get_changes_data, sizeof_fmt)
from .models import NodeSoftwareVersion, State, StateHistory
from .settings import (STATE_NODE_SOFT_VERSION_URL, STATE_NODE_SOFT_VERSION_NAME,
        STATE_FLAPPING_CHANGES, STATE_FLAPPING_MINUTES)
from .views import (report_view, slices_view, slivers_view, get_slices_data,
    get_slivers_data)


STATES_COLORS = dict(NODE_STATES_COLORS)
STATES_COLORS.update({
    State.OFFLINE: 'red',
    State.CRASHED: 'red',
    State.UNKNOWN: 'grey',
    State.NODATA: 'purple',
    'registered': SLIVER_STATES_COLORS[Slice.REGISTER],
    'deployed': SLIVER_STATES_COLORS[Slice.DEPLOY],
    'started': SLIVER_STATES_COLORS[Slice.START],
    'fail_allocate': 'red',
    'fail_deploy': 'red',
    'fail_start': 'red',
})


def display_metadata(instance):
    style = '<style>code,pre {font-size:1.13em;}</style><p></p>'
    metadata = break_headers(instance.metadata)
    metadata = highlight(metadata, JsonLexer(), HtmlFormatter())
    return mark_safe(style + urlize(metadata))
display_metadata.short_description = 'metadata'


def display_data(instance):
    if not instance.data:
        return ''
    style = '<style>code,pre {font-size:1.13em;}</style><p></p>'
    try:
        data = json.dumps(json.loads(instance.data), indent=4, ensure_ascii=False)
    except ValueError: # data is not a valid json string
        data = instance.data
    data = break_lines(data)
    data = highlight(data, JsonLexer(), HtmlFormatter())
    return mark_safe(style + urlize(data))
display_data.short_description = 'data'


def display_current(instance):
    state = instance.current
    style = 'color:%s;' % STATES_COLORS.get(state, "black")
    flapping = ''
    unverified = ''
    
    # Include error messages (if any) as tooltip
    try:
        errors = json.loads(instance.data).get('errors', [])
    except ValueError:
        error_msg = ''
    else:
        error_msg = '\n'.join([error.get('message', '') for error in errors])
        error_msg = escape(error_msg).replace('\n', '&#10;')
    
    # check if the current state match with the defined ones
    try:
        state = filter(lambda s: s[0] == instance.current, State.STATES)[0][1]
    except IndexError:
        # This situation can happen on State renames like on #385 and no data
        # migration is applied to existing objects (ignore, not a big issue)
        state += '?'
    
    # check if state is flapping
    start = timezone.now() - datetime.timedelta(minutes=STATE_FLAPPING_MINUTES)
    changes = instance.history.filter(start__gt=start).count()
    if changes >= STATE_FLAPPING_CHANGES:
        context = (changes, STATE_FLAPPING_MINUTES)
        flapping = 'This state is flapping (%i/%imin)' % context
        state += '*'
    
    # warn about failed verification of SSL certificate
    if (not instance.ssl_verified and
        instance.value not in [State.OFFLINE, State.NODATA, State.UNKNOWN]):
        style += 'text-decoration:line-through;'
        unverified = '(verification failed)'
    
    if not unverified and not flapping:
        state = '<b>%s</b>' % state
    
    context = {
        'flapping': flapping,
        'unverified': unverified,
        'error_msg': error_msg,
    }
    title = "%(flapping)s %(unverified)s\n%(error_msg)s" % context
    return '<span style="%s" title="%s">%s</span>' % (style, title, state)


class StateHistoryAdmin(PermissionModelAdmin):
    list_display = [
        'state', 'display_value', 'display_start_date', 'display_end_date', 'duration'
    ]
    list_display_links = ['state']
    actions = None
    deletable_objects_excluded = True
    
    def get_list_display(self, request):
        list_display = super(StateHistoryAdmin, self).get_list_display(request)
        if hasattr(request, 'state_id'):
            return list_display[1:]
        return list_display
    
    def display_value(self, instance):
        value = colored('value', STATES_COLORS, verbose=True)(instance)
        url = reverse('admin:state_history_data', args=[instance.pk])
        return mark_safe('<a class="show-popup" href="#" url="%s">%s</a>' % (url, value))
    
    def display_start_date(self, instance):
        time = instance.start.strftime('%b. %d, %Y, %I:%M %P')
        time_since = timesince(instance.start)
        return mark_safe('<span title="%s ago">%s</span>' % (time_since, time))
    display_start_date.admin_order_field = 'start'
    display_start_date.short_description = 'Started Date/time'
    
    def display_end_date(self, instance):
        time = instance.end.strftime('%b. %d, %Y, %I:%M %P')
        time_since = timesince(instance.end)
        return mark_safe('<span title="%s ago">%s</span>' % (time_since, time))
    display_end_date.admin_order_field = 'end'
    display_end_date.short_description = 'Ended Date/time'
    
    def duration(self, instance):
        delta = instance.end-instance.start
        seconds = int(delta.total_seconds())
        if seconds < 60:
            context = (delta.seconds, 'second')
        elif seconds < 3600:
            context = ((delta.seconds//60)%60, 'minute')
        elif seconds < 86400:
            context = (delta.seconds//3600, 'hour')
        else:
            context = (delta.days, 'day')
        return "%i %s" % context if context[0] == 1 else "%i %ss" % context
    
    def get_changelist(self, request, **kwargs):
        """ Filter changelist by object """
        from django.contrib.admin.views.main import ChangeList
        class ObjectChangeList(ChangeList):
            def get_queryset(self, *args, **kwargs):
                qs = super(ObjectChangeList, self).get_queryset(*args, **kwargs)
                if hasattr(request, 'state_id'):
                    return qs.filter(state=request.state_id)
                return qs
        return ObjectChangeList
    
    def changelist_view(self, request, *args, **kwargs):
        """ Provide ping action """
        object_id = kwargs.get('object_id')
        request.state_id = object_id
        state = get_object_or_404(State, pk=object_id)
        related_obj_link = get_admin_link(state.content_object)
        context = kwargs.get('extra_context', {})
        context.update({
            'title': mark_safe('State history (%s)' % related_obj_link),
            'header_title': 'State history',
            'obj_opts': state.content_object._meta,
            'obj': state.content_object,
            'ip_addr': state.get_node().mgmt_net.addr,
        })
        return super(StateHistoryAdmin, self).changelist_view(request, extra_context=context)
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def data_view(self, request, object_id):
        history = get_object_or_404(StateHistory, pk=object_id)
        data = {
            'metadata': display_metadata(history) or "(None)",
            'data': display_data(history) or "(None)"
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def changes_view(self, request, object_id):
        state = get_object_or_404(State, pk=object_id)
        data = get_changes_data(state)
        return HttpResponse(json.dumps(data), content_type="application/json")


class StateAdmin(ChangeViewActions, PermissionModelAdmin):
    list_display = ['id', 'content_type_link', 'current', 'content_object_link']
    list_filter = (StateContentTypeFilter, 'value',)
    ordering = ('content_type', 'object_id')
    fieldsets = (
        (None, {
            'fields': ('url_link', 'last_seen', 'last_contact', 'last_try',
                       'next_retry', 'last_change', 'current', 'ssl_verified')
        }),
        ('Details', {
            'fields': (display_metadata, display_data)
        }),
    )
    readonly_fields = [
        'url_link', 'last_seen', 'last_try', 'next_retry', 'current', 'last_change',
        display_metadata, display_data, 'last_contact', 'ssl_verified'
    ]
    change_view_actions = [refresh]
    change_form_template = 'admin/state/state/change_form.html'
    
    class Media:
        css = { "all": ("controller/css/github.css",)}
    
    def get_urls(self):
        admin_site = self.admin_site
        history_admin = StateHistoryAdmin(StateHistory, admin_site)
        urls = patterns("",
            url("^(?P<object_id>\d+)/history/changes/$",
                wrap_admin_view(self, history_admin.changes_view),
                name='state_history_changes'),
            url("^(?P<object_id>\d+)/history/data/$",
                wrap_admin_view(self, history_admin.data_view),
                name='state_history_data'),
            url("^(?P<object_id>\d+)/history/$",
                wrap_admin_view(self, history_admin.changelist_view),
                name='state_history'),
            # URLs not wrapped by admin_view for allow anonymous users
            url("^report/$",
                report_view,
                name='state_report'),
            url("^slices/$",
                slices_view,
                name='state_slices'),
            url("^slices.json$",
                get_slices_data,
                name='state_slices_data'),
            url("^slivers/$",
                slivers_view,
                name='state_slivers'),
            url("^slivers.json$",
                get_slivers_data,
                name='state_slivers_data'),
        )
        return urls + super(StateAdmin, self).get_urls()
    
    def url_link(self, instance):
        url = instance.get_url()
        return mark_safe('<a href="%s">%s</a>' % (url, url))
    url_link.short_description = 'Monitored URL'
    
    def last_seen(self, instance):
        return display_timesince(instance.last_seen_on)
    last_seen.help_text = get_help_text(State, 'last_seen_on')
    
    def last_try(self, instance):
        return display_timesince(instance.last_try_on)
    last_try.help_text = get_help_text(State, 'last_try_on')
    
    def last_change(self, instance):
        return display_timesince(instance.last_change_on)
    last_change.help_text = mark_safe('Last time the state has change, '
                                      'see <a href="history/">state history</a>')
    
    def next_retry(self, instance):
        return display_timeuntil(instance.next_retry_on)
    next_retry.help_text = 'Next time the state retrieval operation will be executed'
    
    def current(self, instance):
        state = display_current(instance)
        url = reverse("admin:state_state_history", args=(instance.pk,))
        return mark_safe('<a href="%s">%s</a>' % (url, state))
    display_current.short_description = 'current'
    
    def content_object_link(self, instance):
        ctype = instance.content_type
        url_pattern = "admin:%s_%s_change" % (ctype.app_label, ctype.model)
        url = reverse(url_pattern, args=(instance.object_id,))
        return mark_safe('<a href="%s">%s</a>' % (url, instance.content_object))
    content_object_link.admin_order_field = 'object_id'
    content_object_link.short_description = 'object'
    
    def content_type_link(self, instance):
        ctype = instance.content_type
        url = reverse("admin:%s_%s_changelist" % (ctype.app_label, ctype.model))
        return mark_safe('<a href="%s">%s</a>' % (url, instance.content_type))
    content_type_link.admin_order_field = 'content_type'
    content_type_link.short_description = 'object type'
    
    def has_add_permission(self, request):
        """ Object states can not be manually created """
        return False
    
    def has_delete_permission(self, *args, **kwargs):
        return False
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        state = self.get_object(request, unquote(object_id))
        if state is None:
            raise Http404('State with id "%s" does not exists' % object_id)
        context = {
            'title': 'State',
            'obj_opts': state.content_object._meta,
            'obj': state.content_object,
            'ip_addr': state.get_node().mgmt_net.addr
        }
        context.update(extra_context or {})
        return super(StateAdmin, self).change_view(request, object_id,
                form_url=form_url, extra_context=context)
    
    def last_contact(self, instance):
        return display_timesince(instance.last_contact_on)
    last_contact.help_text = get_help_text(State, 'last_contact_on')
    
    def sliver_link(self, instance):
        """ Link to related sliver used on change_view """
        return mark_safe(get_admin_link(instance.sliver))
    sliver_link.short_description = 'Sliver'


admin.site.register(State, StateAdmin)
admin.site.register(StateHistory, StateHistoryAdmin)


# Monkey Patch section

def state_link(*args):
    obj = args[-1]
    if not obj.pk:
        # Don't know why state_link is ever called without a real object :(
        return
    state = obj.state
    colored = display_current(state)
    url = reverse('admin:state_state_change', args=[state.pk])
    return mark_safe('<a href="%s">%s</a>' % (url, colored))
state_link.short_description = 'Current state'
state_link.admin_order_field = 'state_set__value'


def firmware_version(node):
    try:
        version = node.soft_version.version
    except NodeSoftwareVersion.DoesNotExist:
        return 'No data'
    else:
        if not version:
            return 'No data'
        url = STATE_NODE_SOFT_VERSION_URL(version)
        name = STATE_NODE_SOFT_VERSION_NAME(version)
        return mark_safe('<a href="%s">%s</a>' % (url, name))
firmware_version.admin_order_field = 'soft_version__value'


def disk_available(node):
    try:
        statejs = json.loads(node.state.data)
    except ValueError:
        return 'No data'
    
    disk = extract_disk_available(statejs)
    # convert to human readable
    unit = disk['unit']
    total = sizeof_fmt(disk['total'], unit)
    slv_dflt = sizeof_fmt(disk['slv_dflt'], unit)
    
    return "%s (%s)" % (total, slv_dflt)
disk_available.short_description = mark_safe('<span class="help-text" '
    'title="Disk available reported by the node:\ntotal (default per sliver)" '
    'style="padding-left:0; padding-right:12px">Disk available</span>')



insertattr(Node, 'list_display', disk_available)
insertattr(NodeListAdmin, 'list_display', disk_available)
insertattr(Node, 'list_display', firmware_version)
insertattr(NodeListAdmin, 'list_display', firmware_version)
insertattr(Node, 'list_display', state_link)
insertattr(NodeListAdmin, 'list_display', state_link)
insertattr(Sliver, 'list_display', state_link)

insertattr(Node, 'actions', refresh_state)
insertattr(Sliver, 'actions', refresh_state)
insertattr(Node, 'list_filter', NodeStateListFilter)
insertattr(NodeListAdmin, 'list_filter', NodeStateListFilter)
insertattr(Sliver, 'list_filter', SliverStateListFilter)
insertattr(Node, 'list_filter', FirmwareVersionListFilter)

SliverInline.sliver_state = state_link
SliverInline.readonly_fields.append('sliver_state')
SliverInline.fields.append('sliver_state')

SliverNodeInline.sliver_state = state_link
SliverNodeInline.readonly_fields.append('sliver_state')
SliverNodeInline.fields.append('sliver_state')

node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action(show_state)
sliver_modeladmin = get_modeladmin(Sliver)
sliver_modeladmin.set_change_view_action(show_state)

actions = getattr(SliceSliversAdmin, 'change_view_actions', [])
SliceSliversAdmin.change_view_actions = actions + [show_state]
old_slice_get_urls = SliceAdmin.get_urls
def get_urls(self):
    urls = old_slice_get_urls(self)
    extra_urls = patterns("",
        url("^(?P<slice_id>\d+)/slivers/(?P<object_id>\d+)/state",
            wrap_admin_view(self, wrap_action(show_state,
                    SliceSliversAdmin(Sliver, self.admin_site))),)
    )
    return extra_urls + urls
SliceAdmin.get_urls = get_urls
