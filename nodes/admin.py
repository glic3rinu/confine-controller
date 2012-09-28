from common.admin import link_factory, insert_inline
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.functional import update_wrapper
from django.utils.html import escape
from forms import NodeInlineAdminForm, HostInlineAdminForm
from models import Node, NodeProp, Host, Gateway, Server, ResearchDevice, RdDirectIface
from singleton_models.admin import SingletonModelAdmin


NODE_STATES_COLORS = { 'install_conf': 'black',
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


def researchdevice__arch(node):
    return node.researchdevice.arch
researchdevice__arch.short_description = 'ResearchDevice Arch'
researchdevice__arch.admin_order_field = 'researchdevice__arch'


def colored_set_state(node):
    state = escape(node.set_state)
    color = NODE_STATES_COLORS.get(state, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color, state)
colored_set_state.short_description = 'Set State'
colored_set_state.allow_tags = True
colored_set_state.admin_order_field = 'set_state'

def admin_link(self):
    url = reverse('admin:auth_user_change', args=(self.admin.pk,))
    return '<a href="%s">%s</a>' % (url, self.admin)
admin_link.short_description = "Admin"
admin_link.allow_tags = True
admin_link.admin_order_field = 'admin'


class NodeAdmin(admin.ModelAdmin):
    list_display = ['description', 'id', link_factory('cn_url', description='CN URL'), 
        'researchdevice', researchdevice__arch, colored_set_state, admin_link]
    list_filter = ['researchdevice__arch', 'set_state']
    search_fields = ['description', 'id']
    inlines = [ResearchDeviceInline, NodePropInline]


def node_link(researchdevice):
    url = reverse('admin:nodes_node_change', args=(researchdevice.node.pk,))
    return '<a href="%s">%s</a>' % (url, researchdevice.node)
node_link.short_description = "Node"
node_link.allow_tags = True
node_link.admin_order_field = 'node'


def colored_set_state_node(researchdevice):
    state = escape(researchdevice.node.set_state)
    color = NODE_STATES_COLORS.get(state, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color, state)
colored_set_state_node.short_description = 'Set State'
colored_set_state_node.allow_tags = True
colored_set_state_node.admin_order_field = 'set_state'


class ResearchDeviceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', node_link, link_factory('cn_url', description='CN URL'), 
        'arch', colored_set_state_node]
    list_filter = ['arch', 'node__set_state']
    search_fields = ['uuid', 'node__description']


class ServerAdmin(SingletonModelAdmin):

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

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


class HostAdmin(admin.ModelAdmin):
    list_display = ['description', 'id', admin_link]


admin.site.register(Node, NodeAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(Gateway)
admin.site.register(Server, ServerAdmin)
admin.site.register(ResearchDevice, ResearchDeviceAdmin)


class HostInline(admin.TabularInline):
    model = Host
    form = HostInlineAdminForm
    max_num = 0


class NodeInline(admin.TabularInline):
    model = Node
    form = NodeInlineAdminForm
    max_num = 0

insert_inline(User, HostInline)
insert_inline(User, NodeInline)
