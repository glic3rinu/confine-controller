from admin_tools.menu import items, Menu
from django.core.urlresolvers import reverse
from controller import settings


def api_link():
    if 'opts' in context: opts = context['opts']
    elif 'cl' in context: opts = context['cl'].opts
    else: return reverse('base')
    if 'object_id' in context: 
        object_id = context['object_id']
        try: return reverse('%s-detail' % opts.module_name, args=[object_id])
        except: return reverse('base')
    try: return reverse('%s-list' % opts.module_name)
    except: return reverse('base')


class CustomMenu(Menu):
    def init_with_context(self, context):
        self.children += [
            items.MenuItem('Dashboard', reverse('admin:index')),
            items.Bookmarks(),]
        
        self.children.append(items.MenuItem('Nodes', reverse('admin:nodes_node_changelist')))
        
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
        
        administration_models = ('django.contrib.auth.*', 'auth_extensions.*', 'djcelery.*')
        
        if 'issues' in settings.INSTALLED_APPS:
            administration_models += ('issues.*',)
            
        if 'firmware' in settings.INSTALLED_APPS:
            administration_models += ('firmware.*',)
            
        self.children.append(items.AppList(
            'Administration',
            models=administration_models
            ))
        
        self.children += [
                    items.MenuItem('API', api_link),
                    items.MenuItem('Documentation', 'http://wiki.confine-project.eu/soft:server'),]
