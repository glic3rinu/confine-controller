from admin_tools.menu import items, Menu
from django.core.urlresolvers import reverse

from controller.utils import is_installed


def _api_link(context):
    """ Dynamically generates API related URL """
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
        user = context['user']
        
        self.children += [
            items.MenuItem('Dashboard', reverse('admin:index')),
            items.Bookmarks(),]
        
        if is_installed('nodes') and user.has_module_perms('nodes'):
            self.children.append(
                items.MenuItem('Nodes',
                    reverse('admin:nodes_node_changelist'),
                    children=[
                        items.MenuItem('Nodes',
                            reverse('admin:nodes_node_changelist')),
                        items.MenuItem('Server',
                            reverse('admin:nodes_server_changelist')),
                    ]))
        
        if is_installed('slices') and user.has_module_perms('slices'):
            self.children.append(items.MenuItem('Slices',
                reverse('admin:slices_slice_changelist'),
                children=[
                    items.MenuItem('Slices',
                        reverse('admin:slices_slice_changelist')),
                    items.MenuItem('Slivers',
                        reverse('admin:slices_sliver_changelist')),
                    items.MenuItem('Templates',
                        reverse('admin:slices_template_changelist')),
                ]))
        
        if is_installed('mgmtnetworks.tinc'):
            if user.is_superuser:
                self.children.append(items.MenuItem('Tinc',
                    reverse('admin:app_list', args=['tinc']),
                    children=[
                        items.MenuItem('Gateways',
                            reverse('admin:tinc_gateway_changelist')),
                        items.MenuItem('Islands',
                            reverse('admin:tinc_island_changelist')),
                        items.MenuItem('TincAddresses',
                            reverse('admin:tinc_tincaddress_changelist')),
                        items.MenuItem('Hosts',
                            reverse('admin:tinc_host_changelist')),
                    ]))
            elif user.has_module_perms('tinc'):
                self.children.append(
                    items.MenuItem('Tinc Hosts',
                        reverse('admin:tinc_host_changelist')))
        
        if user.is_superuser:
            administration_models = ()
            
            if is_installed('djcelery'):
                administration_models += ('djcelery.*',)
            
            if is_installed('issues'):
                administration_models += ('issues.*',)
                
            if is_installed('firmware'):
                administration_models += ('firmware.*',)
            
            admin_item = items.AppList('Administration', models=administration_models)
            
            # Users menu item
            user_items = [
                items.MenuItem('User',
                    reverse('admin:users_user_changelist')),
                items.MenuItem('Group',
                    reverse('admin:users_group_changelist'))
            ]
            
            if is_installed('registration'):
                user_items.append(
                    items.MenuItem('User Registration',
                        reverse('admin:registration_registrationprofile_changelist')))
            
            if is_installed('groupregistration'):
                user_items.append(
                    items.MenuItem('Group registration',
                        reverse('admin:groupregistration_groupregistration_changelist'))
                )
            
            admin_item.children.append(
                items.MenuItem('Users',
                    reverse('admin:app_list', args=['users']),
                    children=user_items)
            )
            
            if is_installed('maintenance'):
                maintenance_items = [
                    items.MenuItem('Operation',
                        reverse('admin:maintenance_operation_changelist')),
                    items.MenuItem('Instance',
                        reverse('admin:maintenance_instance_changelist'))
                ]
                admin_item.children.append(
                    items.MenuItem('Maintenance',
                        reverse('admin:app_list', args=['maintenance']),
                        children=maintenance_items)
                    )
            
        else:
            admin_item = items.MenuItem('Administration',
                children=[
                    items.MenuItem('Users',
                        reverse('admin:users_user_changelist')),
                    items.MenuItem('Groups',
                        reverse('admin:users_group_changelist')),
                    items.MenuItem('Tickets',
                        reverse('admin:issues_ticket_changelist'))
                ])
        
        self.children.append(admin_item)
        
        if is_installed('api'):
            self.children.append(items.MenuItem('API', _api_link(context)))
        
        self.children.append(items.MenuItem('Documentation',
            'http://wiki.confine-project.eu/soft:server'))

