from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import transaction, models
from singleton_models.admin import SingletonModelAdmin

from common.admin import (link, insert_inline, colored, ChangeViewActionsMixin,
    admin_link)
from nodes.actions import request_cert, reboot_selected
from nodes.forms import NodeInlineAdminForm
from nodes.models import Node, NodeProp, Server, DirectIface


STATES_COLORS = { 
    Node.INSTALL_CONF: 'black',
    Node.INSTALL_CERT: 'grey',
    Node.DEBUG: 'darkorange',
    Node.FAILURE: 'red',
    Node.SAFE: 'grey',
    Node.PRODUCTION: 'green', }


def cndb_cached_on(instance):
    date = instance.cndb_cached_on
    if date is None: return 'Never'
    return date
cndb_cached_on.short_description=Node._meta.get_field_by_name('cndb_cached_on')[0].verbose_name


class NodePropInline(admin.TabularInline):
    model = NodeProp
    extra = 0


class DirectIfaceInline(admin.TabularInline):
    model = DirectIface
    extra = 0


class NodeAdmin(ChangeViewActionsMixin):
    list_display = ['description', 'id', 'uuid', link('cn_url', description='CN URL'), 
                    'arch', colored('set_state', STATES_COLORS), admin_link('admin'), 
                    'num_ifaces']
    list_display_links = ('id', 'uuid', 'description')
    list_filter = ['arch', 'set_state']
    search_fields = ['description', 'id', 'uuid']
    readonly_fields = [cndb_cached_on, 'boot_sn']
    inlines = [NodePropInline, DirectIfaceInline]
    fieldsets = (
        (None, {
            'fields': ('description', 'cn_url', ('cndb_uri', cndb_cached_on), 
                       'admin', 'sliver_pub_ipv4_total', 'arch', 'local_iface', 
                       'boot_sn', 'set_state',),
        }),
        ('Keys', {
            'classes': ('collapse',),
            'fields': ('pubkey', 'cert')
        }),
        ('Optional Prefixes', {
            'classes': ('collapse',),
            'fields': ('priv_ipv4_prefix', 'sliver_mac_prefix')
        }),)
    actions = [request_cert, reboot_selected]
    change_view_actions = [('reboot', reboot_selected, '', ''),
                           ('request-cert', request_cert, 'Request Certificate', ''),]
    
    def num_ifaces(self, node):
        return node.directiface_set.count()
    num_ifaces.short_description = 'Ifaces'
    num_ifaces.admin_order_field = 'directiface__count'
    
    def get_form(self, request, *args, **kwargs):
        """ request.user as default node admin """
        form = super(NodeAdmin, self).get_form(request, *args, **kwargs)
        form.base_fields['admin'].initial = request.user
        return form
    
    def queryset(self, request):
        qs = super(NodeAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('directiface'))
        return qs


class ServerAdmin(ChangeViewActionsMixin, SingletonModelAdmin):
    fields = ['cn_url', 'cndb_uri', cndb_cached_on]
    readonly_fields = [cndb_cached_on]
    
    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns = patterns('',
            url(r'^history/$', 
                self.history_view, {'object_id': '1'},
                name='%s_%s_history' % info),
            url(r'^(?P<object_id>\d+)$',
                self.change_view, 
                name='%s_%s_change' % info),
            url(r'^$',
                self.change_view, {'object_id': '1'}, 
                name='%s_%s_changelist' % info),
        )
        urls = super(ServerAdmin, self).get_urls()
        return urlpatterns + urls


admin.site.register(Node, NodeAdmin)
admin.site.register(Server, ServerAdmin)


# Monkey-Patching Section

class NodeInline(admin.TabularInline):
    model = Node
    form = NodeInlineAdminForm
    max_num = 0

insert_inline(User, NodeInline)
