from __future__ import absolute_import

import datetime
import json
import re
import time
from dateutil.relativedelta import relativedelta

from django.contrib import admin
from django.contrib.admin.util import unquote
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_text
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
from nodes.models import Node
from permissions.admin import PermissionModelAdmin
from slices.admin import SliverInline, NodeListAdmin, SliceSliversAdmin, SliceAdmin
from slices.helpers import wrap_action
from slices.models import Sliver

from .actions import refresh, refresh_state, show_state
from .filters import NodeStateListFilter, SliverStateListFilter
from .helpers import break_headers, break_lines
from .models import State, StateHistory, NodeSoftwareVersion
from .settings import STATE_NODE_SOFT_VERSION_URL, STATE_NODE_SOFT_VERSION_NAME


STATES_COLORS = {
    'offline': 'red',
    'crashed': 'red',
    'debug': 'darkorange',
    'safe': 'grey',
    'production': 'green',
    'failure': 'red',
    'online': 'green',
    'unknown': 'grey',
    'registered': 'grey',
    'deployed': 'darkorange',
    'started': 'green',
    'fail_alloc': 'red',
    'fail_deploy': 'red',
    'fail_start': 'red'
}


class StateHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'state', colored('value', STATES_COLORS, verbose=True), 'display_start_date',
        'display_end_date', 'duration'
    ]
    list_display_links = ['state']
    actions = None
    deletable_objects_excluded = True
    
    def get_list_display(self, request):
        list_display = super(StateHistoryAdmin, self).get_list_display(request)
        if hasattr(request, 'state_id'):
            return list_display[1:]
        return list_display
    
    def display_start_date(self, instance):
        time = instance.start.strftime('%b. %d, %Y, %I:%M %P')
        time_since = timesince(instance.start)
        return mark_safe('<span title="%s">%s</span>' % (time_since, time))
    display_start_date.admin_order_field = 'start'
    display_start_date.short_description = 'Started Date/time'
    
    def display_end_date(self, instance):
        time = instance.end.strftime('%b. %d, %Y, %I:%M %P')
        time_since = timesince(instance.end)
        return mark_safe('<span title="%s">%s</span>' % (time_since, time))
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
            def get_query_set(self, *args, **kwargs):
                qs = super(ObjectChangeList, self).get_query_set(*args, **kwargs)
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
    
    def changes_view(self, request, object_id):
        state = get_object_or_404(State, pk=object_id)
        history = state.history
        now = timezone.now()
        delta = relativedelta(months=+1)
        final = datetime.datetime(year=now.year, month=now.month+1, day=1, tzinfo=timezone.utc)
        monthly = {}
        distinct_states = set()
        # Get monthly changes
        for m in range(1, 13):
            initial = final-delta
            changes = history.filter(start__lt=final, end__gt=initial)
            if not changes:
                break
            states = {}
            for value, start, end in changes.values_list('value', 'start', 'end'):
                distinct_states = distinct_states.union(set((value,)))
                if start < initial:
                    start = initial
                if end > final:
                    end = final
                duration = int((end-start).total_seconds())
                states[value] = states.get(value, 0)+duration
            monthly[initial.strftime("%B")] = states
            final = initial
        # Fill missing states
        data = {}
        for month, duration in monthly.iteritems():
            current_states = set()
            for state in duration:
                data.setdefault(state, []).append(duration[state])
                current_states = current_states.union(set((state,)))
            for missing in distinct_states-current_states:
                data.setdefault(state, []).append(0)
        # Construct final data structure
        series = []
        for state in data:
            series.append({
                'name': state,
                'data': data[state],
            })
        data = {
            'categories': list(monthly.keys()),
            'series': series
        }
        return HttpResponse(json.dumps(data), content_type="application/json")


class StateAdmin(ChangeViewActions, PermissionModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('url_link', 'last_seen', 'last_contact',
                       'last_try', 'next_retry', 'last_change', 'current')
        }),
        ('Details', {
            'fields': ('display_metadata', 'display_data')
        }),
    )
    readonly_fields = [
        'url_link', 'last_seen', 'last_try', 'next_retry', 'current', 'last_change',
        'display_metadata', 'display_data', 'last_contact'
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
            url("^(?P<object_id>\d+)/history/$",
                wrap_admin_view(self, history_admin.changelist_view),
                name='state_history'),
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
    
    def display_metadata(self, instance):
        style = '<style>code,pre {font-size:1.13em;}</style><br>'
        metadata = break_headers(instance.metadata)
        metadata = highlight(metadata, JsonLexer(), HtmlFormatter())
        return mark_safe(style + urlize(metadata))
    display_metadata.short_description = 'metadata'
    
    def display_data(self, instance):
        style = '<style>code,pre {font-size:1.13em;}</style><br>'
        # TODO render data according to header content-type
        #      (when it becomes available in the node)
        data = break_lines(instance.data)
        data = highlight(data, JsonLexer(), HtmlFormatter())
        return mark_safe(style + urlize(data))
    display_data.short_description = 'data'
    
    def current(self, instance):
        state = colored('current', STATES_COLORS, verbose=True)(instance)
        try:
            errors = json.loads(instance.data).get('errors', '')
        except ValueError:
            errors = ''
        else:
            errors = str(errors)[2:-2].replace("u'", "'")
        return mark_safe('<a href="history" title="%s">%s</a>' % (errors, state))
    
    def has_add_permission(self, request):
        """ Object states can not be manually created """
        return False
    
    def has_delete_permission(self, *args, **kwargs):
        return False
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        state = get_object_or_404(self.model, pk=object_id)
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
    color = colored('current', STATES_COLORS, verbose=True)
    state = obj.state
    model_name = obj._meta.verbose_name_raw
    url = reverse('admin:state_state_change', args=[state.pk])
    return mark_safe('<a href="%s">%s</a>' % (url, color(state)))
state_link.short_description = 'Current state'
state_link.admin_order_field = 'state_set__value'


def firmware_version(node):
    try:
        version = node.soft_version.value
    except NodeSoftwareVersion.DoesNotExist:
        return 'No data'
    else:
        if not version:
            return 'No data'
        url = STATE_NODE_SOFT_VERSION_URL(version)
        name = STATE_NODE_SOFT_VERSION_NAME(version)
        return mark_safe('<a href="%s">%s</a>' % (url, name))
firmware_version.admin_order_field = 'soft_version'


insertattr(Node, 'list_display', firmware_version)
insertattr(NodeListAdmin, 'list_display', firmware_version)
insertattr(Node, 'list_display', state_link)
insertattr(NodeListAdmin, 'list_display', state_link)
insertattr(Sliver, 'list_display', state_link)

insertattr(Node, 'actions', refresh_state)
insertattr(Sliver, 'actions', refresh_state)
insertattr(Node, 'list_filter', NodeStateListFilter)
insertattr(Sliver, 'list_filter', SliverStateListFilter)
insertattr(Node, 'list_filter', 'soft_version__value')
SliverInline.sliver_state = state_link
SliverInline.readonly_fields.append('sliver_state')
SliverInline.fields.append('sliver_state')

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
