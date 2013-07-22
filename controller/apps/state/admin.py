from __future__ import absolute_import

import re

from django.contrib import admin
from django.contrib.admin.util import unquote
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from controller.admin import ChangeViewActions
from controller.admin.utils import (insert_list_display, get_admin_link, colored,
    insert_list_filter, insert_action, get_modeladmin, wrap_admin_view, display_timesince,
    display_timeuntil)
from controller.models.utils import get_help_text
from nodes.models import Node
from permissions.admin import PermissionModelAdmin
from slices.admin import SliverInline, NodeListAdmin, SliceSliversAdmin, SliceAdmin
from slices.helpers import wrap_action
from slices.models import Sliver

from .actions import refresh, refresh_state, show_state
from .filters import NodeStateListFilter, SliverStateListFilter
from .models import NodeState, SliverState, BaseState
from .settings import STATE_NODE_SOFT_VERSION_URL
from .utils import urlize_escaped_html, urlize


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
    'fail_start': 'red' }


class BaseStateAdmin(ChangeViewActions, PermissionModelAdmin):
    readonly_fields = ['url_link', 'last_seen', 'last_try', 'next_retry', 'current',
        'last_change', 'display_metadata', 'display_data']
    change_view_actions = [refresh]
    
    class Media:
        css = { "all": ("controller/css/github.css",
                        "state/admin/css/details.css") }
    
    def url_link(self, instance):
        url = type(instance).get_url(instance.related_object)
        return mark_safe(urlize(url))
    url_link.short_description = 'Monitored URL'
    
    def last_seen(self, instance):
        return display_timesince(instance.last_seen_on)
    last_seen.help_text = get_help_text(BaseState, 'last_seen_on')
    
    def last_try(self, instance):
        return display_timesince(instance.last_try_on)
    last_try.help_text = get_help_text(BaseState, 'last_try_on')
    
    def last_change(self, instance):
        return display_timesince(instance.last_change_on)
    last_change.help_text = get_help_text(BaseState, 'last_change_on')
    
    def next_retry(self, instance):
        return display_timeuntil(instance.next_retry_on)
    next_retry.help_text = 'Next time the state retrieval operation will be executed'
    
    def display_data(self, instance):
        style = '<style>code,pre {font-size:1.13em;}</style><br></br>'
        # TODO render data according to header content-type
        #      (when it becomes available in the node)
        data = highlight(instance.data, JsonLexer(), HtmlFormatter())
        return mark_safe(style + urlize_escaped_html(data))
    display_data.short_description = 'data'
    
    def display_metadata(self, instance):
        style = '<style>code,pre {font-size:1.13em;}</style><br></br>'
        metadata = highlight(instance.metadata, JsonLexer(), HtmlFormatter())
        return mark_safe(style + urlize_escaped_html(metadata))
    display_metadata.short_description = 'metadata'
    
    def current(self, instance):
        return mark_safe(colored('current', STATES_COLORS, verbose=True)(instance))
    
    def has_add_permission(self, request):
        """ Object states can not be manually created """
        return False
    
    def has_delete_permission(self, *args, **kwargs):
        return False
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        state = self.get_object(request, unquote(object_id))
        related_obj = state.get_related_model().objects.get(pk=object_id)
        title = force_text(self.opts.verbose_name).capitalize()
        title += ' (%s)' % get_admin_link(related_obj)
        context = { 'title': mark_safe(title) }
        context.update(extra_context or {})
        return super(BaseStateAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=context)


class NodeStateAdmin(BaseStateAdmin):
    readonly_fields = ['last_contact'] + BaseStateAdmin.readonly_fields
    fieldsets = (
        (None, {
            'fields': ('url_link', 'last_seen', 'last_contact',
                       'last_try', 'next_retry', 'last_change', 'current')
        }),
        ('Details', {
            'fields': ('display_metadata', 'display_data')
        }),)
    change_form_template = 'admin/state/nodestate/change_form.html'
    
    def last_contact(self, instance):
        return display_timesince(instance.last_contact_on)
    last_contact.help_text = get_help_text(NodeState, 'last_contact_on')


class SliverStateAdmin(BaseStateAdmin):
    fieldsets = (
        (None, {
            'fields': ('url_link', 'last_seen', 'last_try',
                       'next_retry', 'last_change', 'current')
        }),
        ('Details', {
            'fields': ('display_metadata', 'display_data')
        }),)
    change_form_template = 'admin/state/sliverstate/change_form.html'
    
    def sliver_link(self, instance):
        """ Link to related sliver used on change_view """
        return mark_safe(get_admin_link(instance.sliver))
    sliver_link.short_description = 'Sliver'


admin.site.register(NodeState, NodeStateAdmin)
admin.site.register(SliverState, SliverStateAdmin)


# Monkey Patch section

def state_link(*args):
    obj = args[-1]
    if not obj.pk:
        # Don't know why state_link is called without a real object :(
        return
    color = colored('current', STATES_COLORS, verbose=True)
    try:
        state = obj.state
    except NodeState.DoesNotExist:
        state = NodeState.objects.create(node=obj)
    except SliverState.DoesNotExist:
        state = SliverState.objects.create(sliver=obj)
    model_name = obj._meta.verbose_name_raw
    url = reverse('admin:state_%sstate_change' % model_name, args=[state.pk])
    return mark_safe('<a href="%s">%s</a>' % (url, color(state)))
state_link.admin_order_field = 'state__last_seen_on'


def soft_version(node):
    try:
        version = node.state.soft_version
    except NodeState.DoesNotExist:
        return 'No data'
    else:
        if not version:
            return 'No data'
        url = STATE_NODE_SOFT_VERSION_URL(version)
        return mark_safe('<a href="%s">%s</a>' % (url, version))
soft_version.admin_order_field = 'state__soft_version'


insert_list_display(Node, soft_version)
insert_list_display(NodeListAdmin, soft_version)
insert_list_display(Node, state_link)
insert_list_display(NodeListAdmin, state_link)
insert_list_display(Sliver, state_link)
insert_action(Node, refresh_state)
insert_action(Sliver, refresh_state)
insert_list_filter(Node, NodeStateListFilter)
insert_list_filter(Sliver, SliverStateListFilter)
insert_list_filter(Node, 'state__soft_version')
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
