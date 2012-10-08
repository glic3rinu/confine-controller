from common.admin import link, insert_inline, admin_link, colored
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.functional import update_wrapper
from nodes.forms import NodeInlineAdminForm
from nodes.models import Node, NodeProp, Server, ResearchDevice, RdDirectIface
from singleton_models.admin import SingletonModelAdmin


STATES_COLORS = { 'install_conf': 'black',
                  'install_cert': 'grey',
                  'debug': 'darkorange',
                  'failure': 'red',
                  'safe': 'grey',
                  'production': 'green', }


class NodePropInline(admin.TabularInline):
    model = NodeProp
    extra = 0


class ResearchDeviceInline(admin.StackedInline):
    model = ResearchDevice
    max_num = 0


class RdDirectIfaceInline(admin.TabularInline):
    model = RdDirectIface
    extra = 0


def researchdevice__arch(node):
    return node.researchdevice.arch
researchdevice__arch.short_description = 'ResearchDevice Arch'
researchdevice__arch.admin_order_field = 'researchdevice__arch'


class NodeAdmin(admin.ModelAdmin):
    list_display = ['description', 'id', link('cn_url', description='CN URL'), 
        admin_link('researchdevice'), researchdevice__arch, 
        colored('set_state', STATES_COLORS), admin_link('admin')]
    list_filter = ['researchdevice__arch', 'set_state']
    search_fields = ['description', 'id']
    inlines = [ResearchDeviceInline, NodePropInline]


class ResearchDeviceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', admin_link('node'),
        link('cn_url', description='CN URL'), 'arch', 
        colored('node__set_state', STATES_COLORS)]
    list_filter = ['arch', 'node__set_state']
    search_fields = ['uuid', 'node__description']
    inlines = [RdDirectIfaceInline]
    fieldsets = (
        (None, {
            'fields': ('cn_url', 'cndb_uri', 'cndb_cached_on', 'node', 'arch', 
                       'boot_sn', 'local_iface'),
        }),
        ('Keys', {
            'classes': ('collapse',),
            'fields': ('pubkey', 'cert')
        }),)

class ServerAdmin(SingletonModelAdmin):
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^history/$',
                wrap(self.history_view),
                {'object_id': '1'},
                name='%s_%s_history' % info),
            url(r'^$',
                wrap(self.change_view),
                {'object_id': '1'},
                name='%s_%s_change' % info),
            url(r'^$',
                wrap(self.change_view),
                {'object_id': '1'},
                name='%s_%s_changelist' % info),
        )
        return urlpatterns


admin.site.register(Node, NodeAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(ResearchDevice, ResearchDeviceAdmin)


class NodeInline(admin.TabularInline):
    model = Node
    form = NodeInlineAdminForm
    max_num = 0


insert_inline(User, NodeInline)
