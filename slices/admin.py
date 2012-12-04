from __future__ import absolute_import

from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from common.admin import (ChangeViewActionsModelAdmin, colored, admin_link, link,
    insert_list_display, action_to_view, get_modeladmin, wrap_admin_view)
from nodes.admin import NodeAdmin, STATES_COLORS
from nodes.models import Node
from permissions.admin import PermissionModelAdmin, PermissionTabularInline

from .actions import renew_selected_slices, reset_selected
from .filters import MySlicesListFilter, MySliversListFilter
from .forms import SliceAdminForm, IsolatedIfaceInlineForm
from .helpers import wrap_action, remove_slice_id
from .models import (Sliver, SliverProp, IsolatedIface, MgmtIface, PrivateIface,
    Pub6Iface, Pub4Iface, Slice, SliceProp, Template)


STATE_COLORS = { 
    Slice.REGISTER: 'grey',
    Slice.INSTANTIATE: 'darkorange',
    Slice.ACTIVATE: 'green' }


def num_slivers(instance):
    return instance.sliver_set.count()
num_slivers.short_description = 'Slivers'
num_slivers.admin_order_field = 'sliver__count'


def template_link(instance):
    return admin_link('template')(instance)


class SliverPropInline(PermissionTabularInline):
    model = SliverProp
    extra = 0


class IsolatedIfaceInline(PermissionTabularInline):
    model = IsolatedIface
    extra = 0
    form = IsolatedIfaceInlineForm
    verbose_name_plural = 'Isolated Network Interfaces'
    
    def get_formset(self, request, obj=None, **kwargs):
        """ Hook node for future usage in the inline form """
        self.form.node = request._node_
        return super(IsolatedIfaceInline, self).get_formset(request, obj=obj, **kwargs)


class MgmtIfaceInline(PermissionTabularInline):
    model = MgmtIface
    extra = 0
    readonly_fields = ('ipv6_addr',)
    verbose_name_plural = 'Management Network Interfaces'


class PrivateIfaceInline(PermissionTabularInline):
    model = PrivateIface
    extra = 0
    readonly_fields = ('ipv4_addr', 'ipv6_addr')
    verbose_name_plural = 'Private Network Interface'


class Pub6IfaceInline(PermissionTabularInline):
    model = Pub6Iface
    extra = 0
    verbose_name_plural = 'Public IPv6 Interfaces'


class Pub4IfaceInline(PermissionTabularInline):
    model = Pub4Iface
    extra = 0
    verbose_name_plural = 'Public IPv4 Interfaces'


class SliverAdmin(ChangeViewActionsModelAdmin, PermissionModelAdmin):
    list_display = ['__unicode__', admin_link('node'), admin_link('slice'),
                    'has_private_iface', 'num_isolated_ifaces', 'num_pub4_ifaces',
                    'num_pub6_ifaces', 'num_mgmt_ifaces']
    list_filter = [MySliversListFilter, 'slice__name']
    fields = ['description', 'slice_link', 'node_link', 'instance_sn', 'template',
              template_link, 'exp_data', 'exp_data_sha256']
    readonly_fields = ['instance_sn', 'slice_link', 'node_link', 'exp_data_sha256',
                       template_link]
    search_fields = ['description', 'node__description', 'slice__name']
    inlines = [SliverPropInline, PrivateIfaceInline, IsolatedIfaceInline,
               Pub6IfaceInline, Pub4IfaceInline, MgmtIfaceInline]
    actions = [reset_selected]
    change_view_actions = [('reset', reset_selected, '', ''),]
    
    def has_private_iface(self, instance):
        try: instance.privateiface
        except PrivateIface.DoesNotExist: return False
        else: return True
    has_private_iface.short_description = 'Private Iface'
    has_private_iface.boolean = True
    has_private_iface.admin_order_field = 'privateiface'
    
    # Total Interfaces Per Sliver (TIPS) = 256  (unsigned 8)
    #TODO: how many mgmt ifaces can have a sliver? limited by TIPS
    # @url: http://www.grups.pangea.org/pipermail/confine-devel/2012-November/000537.html
    def num_mgmt_ifaces(self, instance):
        #get_ipv6 = lambda iface: iface.ipv6_addr
        #return "<br/> ".join(map(get_ipv6, instance.mgmtiface_set.all()))
        return instance.mgmtiface_set.count()
    num_mgmt_ifaces.short_description = 'Mgmt Ifaces'
    num_mgmt_ifaces.admin_order_field = 'mgmtiface__count'
    
    def num_isolated_ifaces(self, instance):
        return instance.isolatediface_set.count()
    num_isolated_ifaces.short_description = 'Isolated Ifaces'
    num_isolated_ifaces.admin_order_field = 'isolatediface__count'
    
    def num_pub6_ifaces(self, instance):
        return instance.pub6iface_set.count()
    num_pub6_ifaces.short_description = 'Pub IPv6 Ifaces'
    num_pub6_ifaces.admin_order_field = 'pub6iface__count'
    
    def num_pub4_ifaces(self, instance):
        return instance.pub4iface_set.count()
    num_pub4_ifaces.short_description = 'Pub IPv4 Ifaces'
    num_pub4_ifaces.admin_order_field = 'pub4iface__count'

    def slice_link(self, instance):
        return mark_safe("<b>%s</b>" % admin_link('slice')(instance))
    slice_link.short_description = 'Slice'
    
    def node_link(self, instance):
        return mark_safe("<b>%s</b>" % admin_link('node')(instance))
    node_link.short_description = 'Node'
    
    def exp_data_sha256(self, instance):
        return instance.exp_data_sha256
    exp_data_sha256.short_description = 'Experiment Data SHA256'
    
    def queryset(self, request):
        """ Annotate number of ifaces for sorting on the changelist """
        qs = super(SliverAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('isolatediface'))
        qs = qs.annotate(models.Count('pub6iface'))
        qs = qs.annotate(models.Count('pub4iface'))
        qs = qs.annotate(models.Count('isolatediface'))
        qs = qs.annotate(models.Count('mgmtiface'))
        return qs
    
    def has_add_permission(self, *args, **kwargs):
        """ 
        Remove add button on change list. Slivers can only be added from slice change form 
        """
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        """ Hook node reference for future processing in IsolatedIfaceInline """
        request._node_ = obj.node
        return super(SliverAdmin, self).get_form(request, obj, **kwargs)


class NodeListAdmin(NodeAdmin):
    """ 
    Provides a list of available nodes for adding slivers to an existing slice
    """
    list_display = ['add_sliver_link', 'id', 'uuid', link('cn_url', description='CN URL'), 
                    'arch', colored('set_state', STATES_COLORS, verbose=True), admin_link('group'), 
                    'num_ifaces', num_slivers, 'custom_sliver_pub_ipv4_range']
    list_display_links = ['add_sliver_link', 'id', 'uuid']
    # Template that fixes breadcrumbs for the new namespace
    change_list_template = 'admin/slices/slice/list_nodes.html'
    actions = None
    
    def add_sliver_link(self, instance):
        url = reverse('admin:slices_slice_add_sliver', 
                      kwargs={'slice_id':self.slice_id, 'node_id':instance.pk})
        return '<a href="%s">%s<a>' % (url, instance.name)
    add_sliver_link.allow_tags = True
    add_sliver_link.short_description = 'Add on Node'
    
    def custom_sliver_pub_ipv4_range(self, instance):
        return instance.sliver_pub_ipv4_range
    custom_sliver_pub_ipv4_range.short_description = 'IPv4 Range'
    custom_sliver_pub_ipv4_range.admin_order_field = 'sliver_pub_ipv4_range'
    
    def changelist_view(self, request, slice_id, extra_context=None):
        """ Just fixing title and breadcrumbs """
        self.slice_id = slice_id
        slice = Slice.objects.get(pk=slice_id)
        context = {'title': 'Select a node for slice "%s"' % slice.name,
                   'slice': slice, }
        context.update(extra_context or {})
        return super(NodeListAdmin, self).changelist_view(request, extra_context=context)
    
    def queryset(self, request):
        """ Filter node list excluding nodes with already slivers of the slice """
        qs = super(NodeListAdmin, self).queryset(request)
        qs = qs.exclude(pk__in=Node.objects.filter(sliver__slice=self.slice_id))
        qs = qs.annotate(models.Count('sliver'))
        return qs
    
    def has_add_permission(self, *args, **kwargs):
        return False


class SliceSliversAdmin(SliverAdmin):
    """ 
    This ModelAdmin provides Slivers management capabilities on the Slice ModelAdmin
    """
    fields = ['description', 'instance_sn', 'template', 'exp_data', 'exp_data_sha256']
    add_form_template = 'admin/slices/slice/add_sliver.html'
    change_form_template = 'admin/slices/slice/change_sliver.html'
    readonly_fields = ['instance_sn', 'exp_data_sha256']
    
    def add_view(self, request, slice_id, node_id, form_url='', extra_context=None):
        self.slice_id = slice_id
        self.node_id = node_id
        slice = Slice.objects.get(pk=slice_id)
        node = Node.objects.get(pk=node_id)
        context = {'title': 'Add sliver in node "%s" (slice "%s")' % \
                            (node.description, slice.name),
                   'slice': slice,}
        context.update(extra_context or {})
        return super(SliceSliversAdmin, self).add_view(request, form_url='', 
            extra_context=context)
    
    def change_view(self, request, object_id, slice_id, form_url='', extra_context=None):
        slice = Slice.objects.get(pk=slice_id)
        sliver = self.get_object(request, object_id)
        self.slice_id = slice_id
        self.node_id = sliver.node_id
        context = {'title': 'Change sliver in node "%s" (slice "%s")' % \
                            (sliver.node.description, slice.name),
                   'slice': slice,}
        context.update(extra_context or {})
        return super(SliceSliversAdmin, self).change_view(request, object_id, 
            form_url=form_url, extra_context=context)
    
    def save_model(self, request, obj, *args, **kwargs):
        obj.node = Node.objects.get(pk=self.node_id)
        slice = Slice.objects.get(pk=self.slice_id)
        obj.slice = slice
        super(SliceSliversAdmin, self).save_model(request, obj, *args, **kwargs)
        slice_modeladmin = SliceAdmin(slice, self.admin_site)
        slice_modeladmin.log_change(request, slice, 'Added sliver "%s"' % obj)
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        opts = obj._meta
        verbose_name = force_text(opts.verbose_name)
        msg = 'The %s "%s" was added successfully.' % (verbose_name, force_text(obj))
        if "_addanother" in request.POST:
            msg += ' ' + ("You may add another %s below.") % verbose_name
            self.message_user(request, msg)
            return HttpResponseRedirect('../')
        else:
            self.message_user(request, msg)
            if self.has_change_permission(request, None):
                post_url = reverse('admin:slices_slice_change', args=(self.slice_id,))
            else:
                post_url = reverse('admin:index', current_app=self.admin_site.name)
            return HttpResponseRedirect(post_url)
    
    def response_change(self, request, obj):
        opts = obj._meta
        verbose_name = force_text(opts.verbose_name)
        msg = 'The %s "%s" was changed successfully.' % (verbose_name, force_text(obj))
        self.message_user(request, msg)
        if self.has_change_permission(request, None):
            post_url = reverse('admin:slices_slice_change', args=(self.slice_id,))
        else:
            post_url = reverse('admin:index', current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)
    
    def has_add_permission(self, *args, **kwargs):
        return super(SliverAdmin, self).has_add_permission(*args, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        """ Hook node reference for future processing in IsolatedIfaceInline """
        if obj: 
            request._node_ = obj.node
        else:
            # TODO gatting node_id like this is really embarrassing...
            node_id = request.path.split('/')[-2]
            node = Node.objects.get(pk=node_id)
            request._node_ = node
        return super(SliverAdmin, self).get_form(request, obj, **kwargs)


class SliverInline(PermissionTabularInline):
    """ Show slivers in read only fashion """
    model = Sliver
    max_num = 0
    fields = ['sliver_link', 'node_link', 'cn_url']
    readonly_fields = ['sliver_link', 'node_link', 'cn_url']
    
    def sliver_link(self, instance):
        return mark_safe("<b>%s</b>" % admin_link('')(instance))
    sliver_link.short_description = 'Sliver'
    
    def node_link(self, instance):
        return admin_link('node')(instance)
    node_link.short_description = 'Node'
    
    def cn_url(self, instance):
        node = instance.node
        return mark_safe("<a href='%s'>%s</a>" % (node.cn_url, node.cn_url))


class SlicePropInline(PermissionTabularInline):
    model = SliceProp
    extra = 0


class SliceAdmin(ChangeViewActionsModelAdmin, PermissionModelAdmin):
    list_display = ['name', 'uuid', 'vlan_nr', colored('set_state', STATE_COLORS, verbose=True),
                    num_slivers, admin_link('template'), 'expires_on', admin_link('group')]
    list_display_links = ('name', 'uuid')
    list_filter = [MySlicesListFilter, 'set_state', 'template']
#    filter_horizontal = ['users']
    readonly_fields = ['instance_sn', 'new_sliver_instance_sn', 'expires_on', 
                       'exp_data_sha256', template_link]
    date_hierarchy = 'expires_on'
    search_fields = ['name', 'uuid']
    inlines = [SlicePropInline, SliverInline]
    actions = [reset_selected, renew_selected_slices]
    form = SliceAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'description', ('template', template_link), ('exp_data', 
                       'exp_data_sha256'), 'set_state', 'vlan_nr', 
                       'instance_sn', 'new_sliver_instance_sn', 'expires_on',
                       'group'),
        }),
        ('SFA', {
            'classes': ('collapse',),
            'fields': ('pubkey', 'uuid')
        }),)
    change_form_template = "admin/slices/slice/change_form.html"
    change_view_actions = [('renew', renew_selected_slices, '', ''),
                           ('reset', reset_selected, '', '')]
    
    def exp_data_sha256(self, instance):
        return instance.exp_data_sha256
    exp_data_sha256.short_description = 'Experiment Data SHA256'
    
    def queryset(self, request):
        """ 
        Annotate number of slivers on the slice for sorting on changelist 
        """
        qs = super(SliceAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('sliver'))
        return qs
    
    def get_urls(self):
        """ Hook sliver management URLs on slice admin """
        urls = super(SliceAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        extra_urls = patterns("", 
            url("^(?P<slice_id>\d+)/add_sliver/$", 
                wrap_admin_view(self, NodeListAdmin(Node, admin_site).changelist_view), 
                name='slices_slice_add_sliver'),
            url("^(?P<slice_id>\d+)/add_sliver/(?P<node_id>\d+)/$", 
                wrap_admin_view(self, SliceSliversAdmin(Sliver, admin_site).add_view), 
                name='slices_slice_add_sliver'),
            url("^(?P<slice_id>\d+)/slivers/(?P<object_id>\d+)/$", 
                wrap_admin_view(self, SliceSliversAdmin(Sliver, admin_site).change_view), 
                name='slices_slice_slivers'),
            url("^(?P<slice_id>\d+)/slivers/(?P<object_id>\d+)/history", 
                wrap_admin_view(self, remove_slice_id(SliceSliversAdmin(Sliver,
                    admin_site).history_view)),),
            url("^(?P<slice_id>\d+)/slivers/(?P<object_id>\d+)/reset", 
                wrap_admin_view(self, wrap_action(reset_selected, 
                    SliceSliversAdmin(Sliver, admin_site))),)
        )
        return extra_urls + urls
    
    def get_form(self, request, *args, **kwargs):
        """ request.user as default node admin """
        form = super(SliceAdmin, self).get_form(request, *args, **kwargs)
        if 'group' in form.base_fields:
            # ronly forms doesn't have initial nor queryset
            user = request.user
            groups = user.groups.filter(roles__is_admin=True)
            num_groups = groups.count()
            if num_groups >= 1:
                form.base_fields['group'].queryset = groups
            if num_groups == 1:
                form.base_fields['group'].initial = groups[0]
        return form


class TemplateAdmin(PermissionModelAdmin):
    list_display = ['name', 'description', 'type', 'arch', 'image', 'is_active']
    list_filter = ['is_active', 'type', 'arch']
    search_fields = ['name', 'description', 'type', 'arch']
    fields = ['name', 'description', 'type', 'arch', 'image', 'image_sha256', 
              'is_active']
    readonly_fields = ['image_sha256']
    
    def image_sha256(self, instance):
        return instance.image_sha256
    image_sha256.short_description = 'Image SHA256'


admin.site.register(Sliver, SliverAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Template, TemplateAdmin)


# Monkey-Patching Section

node_modeladmin = get_modeladmin(Node)
old_queryset = node_modeladmin.queryset

def queryset(request):
    " Annotate number of slivers for sorting on node changelist "
    qs = old_queryset(request)
    qs = qs.annotate(models.Count('sliver'))
    return qs

node_modeladmin.queryset = queryset

insert_list_display(Node, num_slivers)
