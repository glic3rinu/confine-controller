from common.admin import (ChangeViewActionsMixin, colored, admin_link, link,
    insert_list_display, action_to_view, get_modeladmin)
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from nodes.admin import NodeAdmin, STATES_COLORS
from nodes.models import Node
from slices.actions import renew_selected_slices, reset_selected
from slices.forms import SliceAdminForm
from slices.helpers import wrap_action, remove_slice_id
from slices.models import (Sliver, SliverProp, IsolatedIface, PublicIface, 
    PrivateIface, Slice, SliceProp, Template)


STATE_COLORS = { 'register': 'grey',
                 'instantiate': 'darkorange',
                 'activate': 'green' }


def num_slivers(instance):
    return instance.sliver_set.count()
num_slivers.short_description = 'Slivers'
num_slivers.admin_order_field = 'sliver__count'


class SliverPropInline(admin.TabularInline):
    model = SliverProp
    extra = 0

class IsolatedIfaceInline(admin.TabularInline):
    model = IsolatedIface
    extra = 0
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """ Limit parent choices to those available on the current node """
        field = super(IsolatedIfaceInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'parent':
            field.queryset = field.queryset.filter(node=request._node_)
        return field


class PublicIfaceInline(admin.TabularInline):
    model = PublicIface
    extra = 0


class PrivateIfaceInline(admin.TabularInline):
    model = PrivateIface
    extra = 0


class SliverAdmin(ChangeViewActionsMixin):
    list_display = ['id', 'description', admin_link('node'), admin_link('slice'),
        'has_private_iface', 'num_isolated_ifaces', 'num_public_ifaces']
    list_filter = ['slice__name']
    fields = ['description', 'slice_link', 'node_link', 'instance_sn']
    readonly_fields = ['instance_sn', 'slice_link', 'node_link']
    search_fields = ['description', 'node__description', 'slice__name']
    inlines = [SliverPropInline, IsolatedIfaceInline, PublicIfaceInline, 
               PrivateIfaceInline]
    actions = [reset_selected]
    change_view_actions = [('reset', reset_selected, '', ''),]
    
    def has_private_iface(self, instance):
        try: instance.privateiface
        except PrivateIface.DoesNotExist: return False
        else: return True
    has_private_iface.short_description = 'PrivateIface'
    has_private_iface.boolean = True
    has_private_iface.admin_order_field = 'privateiface'
    
    def num_isolated_ifaces(self, instance):
        return instance.isolatediface_set.count()
    num_isolated_ifaces.short_description = 'IsolatedIfaces'
    num_isolated_ifaces.admin_order_field = 'isolatediface__count'
    
    def num_public_ifaces(self, instance):
        return instance.isolatediface_set.count()
    num_public_ifaces.short_description = 'PublicIfaces'
    num_public_ifaces.admin_order_field = 'publiciface__count'
    
    def slice_link(self, instance):
        url = reverse('admin:slices_slice_change', args=[instance.slice.pk])
        return mark_safe("<b><a href='%s'>%s</a></b>" % (url, instance.slice))
    slice_link.short_description = 'Slice'
    
    def node_link(self, instance):
        url = reverse('admin:nodes_node_change', args=[instance.node.pk])
        return mark_safe("<b><a href='%s'>%s</a></b>" % (url, instance.node))
    node_link.short_description = 'Node'
    
    def queryset(self, request):
        qs = super(SliverAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('isolatediface'))
        qs = qs.annotate(models.Count('publiciface'))
        return qs
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        # just save node reference for future processing in IsolatedIfaceInline
        request._node_ = obj.node
        return super(SliverAdmin, self).get_form(request, obj, **kwargs)

class NodeListAdmin(NodeAdmin):
    """ Provides a list of nodes for adding slivers to an slice"""
    
    # fixing breadcrumbs
    list_display = NodeAdmin.list_display + [num_slivers, 'custom_sliver_pub_ipv4_total']
    change_list_template = 'admin/slices/slice/list_nodes.html'
    actions = None
    
    def custom_sliver_pub_ipv4_total(self, instance):
        return instance.sliver_pub_ipv4_total
    custom_sliver_pub_ipv4_total.short_description = 'Total IPv4'
    custom_sliver_pub_ipv4_total.admin_order_field = 'sliver_pub_ipv4_total'
    
    def changelist_view(self, request, slice_id, extra_context=None):
        self.slice_id = slice_id
        slice = Slice.objects.get(pk=slice_id)
        context = {'title': 'Select a node for slice "%s"' % slice.name,
                   'slice': slice, }
        context.update(extra_context or {})
        return super(NodeListAdmin, self).changelist_view(request, context)
    
    def queryset(self, request):
        """ Filter the node list to nodes where there are no slivers of this slice """
        qs = super(NodeListAdmin, self).queryset(request)
        qs = qs.exclude(pk__in=Node.objects.filter(sliver__slice=self.slice_id))
        qs = qs.annotate(models.Count('sliver'))
        return qs

    def has_add_permission(self, *args, **kwargs):
        return False


class SliceSliversAdmin(SliverAdmin):
    """ Slivers management (add and change) directly from the Slice """
    
    fields = ['description', 'instance_sn']
    add_form_template = 'admin/slices/slice/add_sliver.html'
    change_form_template = 'admin/slices/slice/change_sliver.html'
    readonly_fields = ['instance_sn']
    
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
        self.node_id = sliver.node.pk
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
            return HttpResponseRedirect('.')
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
        # just save node reference for future processing in IsolatedIfaceInline
        node_id = request.path.split('/')[-2]
        node = Node.objects.get(pk=node_id)
        request._node_ = node
        return super(SliceSliversAdmin, self).get_form(request, obj, **kwargs)


class SliverInline(admin.TabularInline):
    model = Sliver
    max_num = 0
    fields = ['sliver_link', 'node_link', 'cn_url']
    readonly_fields = ['sliver_link', 'node_link', 'cn_url']
    
    def sliver_link(self, instance):
        url = reverse('admin:slices_slice_slivers', 
            kwargs={'slice_id': instance.slice.pk, 'object_id': instance.pk})
        return mark_safe("<b><a href='%s'>%s</a></b>" % (url, instance))
    
    def node_link(self, instance):
        url = reverse('admin:nodes_node_change', args=[instance.node.pk])
        return mark_safe("<b><a href='%s'>%s</a></b>" % (url, instance.node))
    
    def cn_url(self, instance):
        node = instance.node
        return mark_safe("<a href='%s'>%s</a>" % (node.cn_url, node.cn_url))


class SlicePropInline(admin.TabularInline):
    model = SliceProp
    extra = 0


class SliceAdmin(ChangeViewActionsMixin):
    list_display = ['name', 'uuid', 'vlan_nr', colored('set_state', STATE_COLORS),
        num_slivers, admin_link('template'), 'expires_on', ]
    list_display_links = ('name', 'uuid')
    list_filter = ['set_state', 'template']
    readonly_fields = ['instance_sn', 'new_sliver_instance_sn', 'expires_on']
    date_hierarchy = 'expires_on'
    search_fields = ['name', 'uuid']
    inlines = [SlicePropInline, SliverInline]
    actions = [reset_selected, renew_selected_slices]
    form = SliceAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'description', ('template', 'exp_data'), 
                       'set_state', 'users', 'vlan_nr', 'instance_sn',
                       'new_sliver_instance_sn', 'expires_on'),
        }),
        ('Public key', {
            'classes': ('collapse',),
            'fields': ('pubkey',)
        }),)
    change_form_template = "admin/slices/slice/change_form.html"
    change_view_actions = [('renew', renew_selected_slices, '', ''),
                           ('reset', reset_selected, '', '')]
    
    def queryset(self, request):
        qs = super(SliceAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('sliver'))
        return qs
    
    def get_urls(self):
        urls = super(SliceAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        # TODO Refactor: Hook SliceSliversAdmin in a clever way
        extra_urls = patterns("", 
            url("^(?P<slice_id>\d+)/add_sliver/$", 
                NodeListAdmin(Node, admin_site).changelist_view, 
                name='slices_slice_add_sliver'),
            url("^(?P<slice_id>\d+)/add_sliver/(?P<node_id>\d+)/$", 
                SliceSliversAdmin(Sliver, admin_site).add_view, 
                name='slices_slice_add_sliver'),
            url("^(?P<slice_id>\d+)/slivers/(?P<object_id>\d+)/$", 
                SliceSliversAdmin(Sliver, admin_site).change_view, 
                name='slices_slice_slivers'),
            url("^(?P<slice_id>\d+)/slivers/(?P<object_id>\d+)/history", 
                remove_slice_id(SliceSliversAdmin(Sliver, admin_site).history_view),),
            url("^(?P<slice_id>\d+)/slivers/(?P<object_id>\d+)/reset", 
                wrap_action(reset_selected, SliceSliversAdmin(Sliver, admin_site)),)
            )
        return extra_urls + urls


class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'type', 'arch', 'data', 'is_active']
    list_filter = ['is_active', 'type', 'arch']
    search_fields = ['name', 'description', 'type', 'arch']


admin.site.register(Sliver, SliverAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Template, TemplateAdmin)


# Monkey-Patching Section

node_modeladmin = get_modeladmin(Node)
old_queryset = node_modeladmin.queryset

def queryset(request):
    qs = old_queryset(request)
    qs = qs.annotate(models.Count('sliver'))
    return qs

node_modeladmin.queryset = queryset

insert_list_display(Node, num_slivers)
