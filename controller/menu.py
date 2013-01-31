from admin_tools.menu import items, Menu
from django.core.urlresolvers import reverse

from common.utils import is_installed


def api_link(context):
    if 'opts' in context:
        opts = context['opts']
    elif 'cl' in context:
        opts = context['cl'].opts
    else:
        return reverse('base')
    if 'object_id' in context: 
        object_id = context['object_id']
        try:
            return reverse('%s-detail' % opts.module_name, args=[object_id])
        except:
            return reverse('base')
    try:
        return reverse('%s-list' % opts.module_name)
    except:
        return reverse('base')


class CustomMenu(Menu):
    def init_with_context(self, context):
        self.children += [
            items.MenuItem('Dashboard', reverse('admin:index')),
            items.Bookmarks(),]
        
        self.children.append(items.MenuItem('Nodes', reverse('admin:nodes_node_changelist')))
        
        if context['user'].has_module_perms('slices'):
            self.children.append(items.MenuItem('Slices', reverse('admin:app_list', args=['slices']),
                children=[
                    items.MenuItem('Slices', reverse('admin:slices_slice_changelist')),
                    items.MenuItem('Slivers', reverse('admin:slices_sliver_changelist')),
                    items.MenuItem('Templates', reverse('admin:slices_template_changelist')),
                ]))
        
        if is_installed('mgmtnetworks.tinc') and context['user'].has_module_perms('tinc'):
            self.children.append(items.MenuItem('Tinc', reverse('admin:app_list', args=['tinc']),
                children=[
                    items.MenuItem('Gateways', reverse('admin:tinc_gateway_changelist')),
                    items.MenuItem('Islands', reverse('admin:tinc_island_changelist')),
                    items.MenuItem('TincAddresses', reverse('admin:tinc_tincaddress_changelist')),
                    items.MenuItem('Hosts', reverse('admin:tinc_host_changelist')),
                ]))
        
        administration_models = ('users.*', 'djcelery.*')
        
        if is_installed('issues'):
            administration_models += ('issues.*',)
            
        if is_installed('firmware'):
            administration_models += ('firmware.*',)
        
        admin_item = items.AppList('Administration', models=administration_models)

        if is_installed('registration'):
            menu_items=[items.MenuItem('User registration', reverse('admin:registration_registrationprofile_changelist'))]
            if  is_installed('groupregistration'):
                menu_items+=[items.MenuItem('Group registration', reverse('admin:groupregistration_groupregistration_changelist')),]

            admin_item.children.append(items.MenuItem('Registration', children=menu_items))

        self.children.append(admin_item)
        
        self.children += [
                    items.MenuItem('API', api_link(context)),
                    items.MenuItem('Documentation', 'http://wiki.confine-project.eu/soft:server'),]

