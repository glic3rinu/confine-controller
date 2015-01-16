from admin_tools.menu import items, Menu
from django.core.urlresolvers import reverse

from controller.utils.apps import is_installed


def api_link(context):
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
            return reverse('%s-detail' % opts.model_name, args=[object_id])
        except:
            return reverse('base')
    try:
        return reverse('%s-list' % opts.model_name)
    except:
        return reverse('base')


class CustomMenu(Menu):
    def init_with_context(self, context):
        user = context['user']
        
        self.children += [
            items.MenuItem('Dashboard', reverse('admin:index')),
            items.Bookmarks(),]
        
        if is_installed('nodes') and user.has_module_perms('nodes'):
            node_items = [
                items.MenuItem('Nodes',
                    reverse('admin:nodes_node_changelist')),
                items.MenuItem('Servers',
                    reverse('admin:nodes_server_changelist')),
                items.MenuItem('Islands',
                    reverse('admin:nodes_island_changelist')),
            ]
            if is_installed('state'):
                node_items.append(
                    items.MenuItem('Summary', reverse('admin:state_report'))
                )
            if is_installed('gis'):
                node_items.insert(
                    1,
                    items.MenuItem('Nodes Map', reverse('gis_map'))
                )
            self.children.append(
                items.MenuItem('Nodes',
                    reverse('admin:nodes_node_changelist'),
                    children=node_items))
        
        if is_installed('slices') and user.has_module_perms('slices'):
            slice_children = sliver_children = None
            if is_installed('state'):
                slice_children = [
                    items.MenuItem('Status Overview',
                        reverse('admin:state_slices')),
                ]
                sliver_children = [
                    items.MenuItem('Status Overview',
                        reverse('admin:state_slivers')),
                ]
            self.children.append(items.MenuItem('Slices',
                reverse('admin:slices_slice_changelist'),
                children=[
                    items.MenuItem('Slices',
                        reverse('admin:slices_slice_changelist'),
                        children=slice_children),
                    items.MenuItem('Slivers',
                        reverse('admin:slices_sliver_changelist'),
                        children=sliver_children),
                    items.MenuItem('Templates',
                        reverse('admin:slices_template_changelist')),
                ]))
        
        if is_installed('tinc'):
            if user.has_module_perms('tinc'):
                self.children.append(items.MenuItem('Tinc',
                    reverse('admin:app_list', args=['tinc']),
                    children=[
                        items.MenuItem('TincAddresses',
                            reverse('admin:tinc_tincaddress_changelist')),
                        items.MenuItem('Hosts',
                            reverse('admin:tinc_host_changelist')),
                    ]))
        
        if user.is_superuser:
            administration_models = ()
            
            if is_installed('djcelery'):
                administration_models += ('djcelery.*',)
            
            admin_item = items.AppList('Administration', models=administration_models)
            
            # Users menu item
            user_items = [
                items.MenuItem('User',
                    reverse('admin:users_user_changelist')),
                items.MenuItem('Group',
                    reverse('admin:users_group_changelist')),
                items.MenuItem('Roles',
                    reverse('admin:users_roles_changelist')),
            ]
            
            if is_installed('registration'):
                user_items.append(
                    items.MenuItem('User Registration',
                        reverse('admin:registration_registrationprofile_changelist')))
            
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
            
            if is_installed('issues'):
                issues_items = [
                    items.MenuItem('Tickets',
                        reverse('admin:issues_ticket_changelist')),
                    items.MenuItem('Queues',
                        reverse('admin:issues_queue_changelist'))
                ]
                admin_item.children.append(
                    items.MenuItem('Issues',
                        reverse('admin:issues_ticket_changelist'),
                        children=issues_items)
                    )
            
            if is_installed('firmware'):
                firmware_items = [
                    items.MenuItem('Configuration',
                        reverse('admin:firmware_config_change')),
                    items.MenuItem('Builds',
                        reverse('admin:firmware_build_changelist'))
                ]
                admin_item.children.append(
                    items.MenuItem('Firmware',
                        reverse('admin:app_list', args=['firmware']),
                        children=firmware_items)
                    )
            
            if is_installed('notifications'):
                admin_item.children.append(
                    items.MenuItem('Notifications',
                        reverse('admin:notifications_notification_changelist')),
                )
        
        else:
            admin_items = [
                items.MenuItem('Users',
                    reverse('admin:users_user_changelist')),
                items.MenuItem('Groups',
                    reverse('admin:users_group_changelist')),
                ]
            if is_installed('issues'):
                admin_items.append(
                    items.MenuItem('Tickets',
                        reverse('admin:issues_ticket_changelist'))
                    )
            admin_item = items.MenuItem('Administration',
                children=admin_items)
        
        self.children.append(admin_item)
        
        if is_installed('api'):
            self.children.append(items.MenuItem('API', api_link(context)))
        
        self.children.append(items.MenuItem('Documentation',
            'http://wiki.confine-project.eu/soft:server'))

