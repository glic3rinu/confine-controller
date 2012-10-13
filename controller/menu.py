from django.core.urlresolvers import reverse
from admin_tools.menu import items, Menu
import settings


class CustomMenu(Menu):
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem('Dashboard', reverse('admin:index')),
            items.Bookmarks(),]

        self.children.append(items.MenuItem('Nodes', '/admin/nodes/',
            children=[
                items.MenuItem('Nodes', reverse('admin:nodes_node_changelist')),
                items.MenuItem('Research Devices', reverse('admin:nodes_researchdevice_changelist')),
                items.MenuItem('Server', reverse('admin:nodes_server_changelist')),
            ]))

        self.children.append(items.MenuItem('Slices', '/admin/slices/',
            children=[
                items.MenuItem('Slices', reverse('admin:slices_slice_changelist')),
                items.MenuItem('Slivers', reverse('admin:slices_sliver_changelist')),
                items.MenuItem('Templates', reverse('admin:slices_template_changelist')),
            ]))

        if 'tinc' in settings.INSTALLED_APPS:
            self.children.append(items.MenuItem('Tinc', '/admin/tinc/',
                children=[
                    items.MenuItem('Gateways', reverse('admin:tinc_gateway_changelist')),
                    items.MenuItem('Islands', reverse('admin:tinc_island_changelist')),
                    items.MenuItem('TincAddresses', reverse('admin:tinc_tincaddress_changelist')),
                    items.MenuItem('Hosts', reverse('admin:tinc_host_changelist')),
                ]))

        self.children.append(items.AppList(
            'Administration',
            models=('django.contrib.auth.*', 'auth_extensions.*', 'issues.*')
            ))

        self.children += [
                    items.MenuItem('API', 'https://controller.confine-project.eu/api'),
                    items.MenuItem('Documentation', 'https://wiki.confine-project.eu/soft:server'),]
