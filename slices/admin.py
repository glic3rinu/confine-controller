from __future__ import absolute_import

from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from common.admin import (ChangeViewActionsModelAdmin, colored, admin_link, link,
    insert_list_display, action_to_view, get_modeladmin, wrap_admin_view, 
    docstring_as_help_tip)
from common.widgets import ReadOnlyWidget
from nodes.admin import NodeAdmin, STATES_COLORS
from nodes.models import Node
from permissions.admin import PermissionModelAdmin, PermissionTabularInline

from .actions import renew_selected_slices, reset_selected, create_slivers
from .filters import MySlicesListFilter, MySliversListFilter
from .forms import SliceAdminForm, SliverIfaceInlineForm
from .helpers import wrap_action, remove_slice_id
from .models import (Sliver, SliverProp, SliverIface, Slice, SliceProp, Template)


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
    verbose_name_plural = mark_safe('Sliver Properties %s' % docstring_as_help_tip(SliverProp))


class SliverIfaceInline(PermissionTabularInline):
    model = SliverIface
    readonly_fields = ['nr', 'ipv6_addr', 'ipv4_addr']
    extra = 0
    verbose_name_plural = mark_safe('Sliver Network Interfaces <a href="http://wiki.confine-project.eu/arch:node">(Help)</a>')
    form = SliverIfaceInlineForm
    
    def get_formset(self, request, obj=None, **kwargs):
        """ Hook node for future usage in the inline form """
        self.form.node = request._node_
        return super(SliverIfaceInline, self).get_formset(request, obj=obj, **kwargs)


class SliverAdmin(ChangeViewActionsModelAdmin, PermissionModelAdmin):
    list_display = ['__unicode__', admin_link('node'), admin_link('slice'), 'total_num_ifaces']
    list_filter = [MySliversListFilter, 'slice__name']
    fields = ['description', 'slice_link', 'node_link', 'instance_sn', 'template',
              template_link, 'exp_data', 'exp_data_sha256']
    readonly_fields = ['instance_sn', 'slice_link', 'node_link', 'exp_data_sha256',
                       template_link]
    search_fields = ['description', 'node__description', 'slice__name']
    inlines = [SliverPropInline, SliverIfaceInline]
    actions = [reset_selected]
    change_view_actions = [('reset', reset_selected, '', ''),]
    
    
    def __init__(self, *args, **kwargs):
        """ Show number of requested ifaces on sliver changelist """
        for iface_type, iface_type_verbose in Sliver.get_registred_iface_types():
            iface = Sliver.get_registred_iface(iface_type)
            if not iface_type in self.list_display and not iface.AUTO_CREATE:
                def display_ifaces(instance, iface_type=iface_type):
                    return instance.sliveriface_set.filter(type=iface_type).count()
                display_ifaces.short_description = iface_type_verbose
                display_ifaces.boolean = True if iface.UNIQUE else False
                setattr(self, iface_type, display_ifaces)
                self.list_display.append(iface_type)
        super(SliverAdmin, self).__init__(*args, **kwargs)
    
    def total_num_ifaces(self, instance):
        return instance.sliveriface_set.count()
    total_num_ifaces.short_description = 'Total Ifaces'
    total_num_ifaces.admin_order_field = 'sliveriface__count'

    def slice_link(self, instance):
        return mark_safe("<b>%s</b>" % admin_link('slice')(instance))
    slice_link.short_description = 'Slice'
    
    def node_link(self, instance):
        return mark_safe("<b>%s</b>" % admin_link('node')(instance))
    node_link.short_description = 'Node'
    
    def exp_data_sha256(self, instance):
        return instance.exp_data_sha256
    exp_data_sha256.short_description = 'Experiment Data SHA256'
    
    def has_add_permission(self, *args, **kwargs):
        """ 
        Remove add button on change list. Slivers can only be added from slice change form 
        """
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        """ Hook node reference for future processing in IsolatedIfaceInline """
        request._node_ = obj.node
        return super(SliverAdmin, self).get_form(request, obj, **kwargs)
    
    def changelist_view(self, request, extra_context=None):
        """ Default filter as 'my_slivers=True' """
        if not request.GET.has_key('my_slivers'):
            q = request.GET.copy()
            q['my_slivers'] = 'True'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(SliverAdmin,self).changelist_view(request, extra_context=extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Provide a linked title """
        sliver = self.get_object(request, object_id)
        context = {'title': mark_safe('Change sliver %s@%s' % \
                                      (admin_link('')(sliver.node), admin_link('')(sliver.slice))),
                   'slice': slice,}
        context.update(extra_context or {})
        return super(SliverAdmin, self).change_view(request, object_id, form_url=form_url, 
                     extra_context=context)
    
    def queryset(self, request):
        """ Annotate number of ifaces for future ordering on the changellist """
        qs = super(SliverAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('sliveriface', distinct=True))
        return qs
    
    def log_addition(self, request, object):
        """ AUTO_CREATE SliverIfaces """
        for iface in Sliver.get_registred_ifaces():
            iface_type = Sliver.get_registred_iface_type(type(iface))
            if iface.AUTO_CREATE and not object.sliveriface_set.filter(type=iface_type).exists():
                SliverIface.objects.create(sliver=object, type=iface_type, name=iface.DEFAULT_NAME)
        super(SliverAdmin, self).log_addition(request, object)


class NodeListAdmin(NodeAdmin):
    """ 
    Provides a list of available nodes for adding slivers to an existing slice
    """
    list_display = ['add_sliver_link', 'id', link('cn_url', description='CN URL'), 
                    'arch', colored('set_state', STATES_COLORS, verbose=True), admin_link('group'), 
                    'num_ifaces', num_slivers, 'custom_sliver_pub_ipv4_range']
    list_display_links = ['add_sliver_link', 'id']
    # Template that fixes breadcrumbs for the new namespace
    change_list_template = 'admin/slices/slice/list_nodes.html'
    
    def add_sliver_link(self, instance):
        url = reverse('admin:slices_slice_add_sliver', 
                      kwargs={'slice_id':self.slice_id, 'node_id':instance.pk})
        return '<a href="%s">%s<a>' % (url, instance.name)
    add_sliver_link.allow_tags = True
    add_sliver_link.short_description = 'Add on Node'
    
    def get_actions(self, request):
        from django.utils.datastructures import SortedDict
        actions = []
        actions.extend([self.get_action(action) for action in [create_slivers]])
        
        # Convert the actions into a SortedDict keyed by name.
        actions = SortedDict([
            (name, (func, name, desc))
            for func, name, desc in actions
        ])
        return actions
    
    def custom_sliver_pub_ipv4_range(self, instance):
        return instance.sliver_pub_ipv4_range
    custom_sliver_pub_ipv4_range.short_description = 'IPv4 Range'
    custom_sliver_pub_ipv4_range.admin_order_field = 'sliver_pub_ipv4_range'
    
    def changelist_view(self, request, slice_id, extra_context=None):
        """ Just fixing title and breadcrumbs """
        self.slice_id = slice_id
        slice = Slice.objects.get(pk=slice_id)
        context = {'title': mark_safe('Select one or more nodes for creating %s slivers' % admin_link('')(slice)),
                   'slice': slice, }
        context.update(extra_context or {})
        # call super.super to avoid my_nodes default changelist filter of NodeAdmin
        return super(NodeAdmin, self).changelist_view(request, extra_context=context)
    
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
        context = {'title': mark_safe('Add sliver %s@%s' % \
                                      (admin_link('')(slice), admin_link('')(node))),
                   'slice': slice,}
        context.update(extra_context or {})
        return super(SliceSliversAdmin, self).add_view(request, form_url='', 
            extra_context=context)
    
    def change_view(self, request, object_id, slice_id, form_url='', extra_context=None):
        slice = Slice.objects.get(pk=slice_id)
        sliver = self.get_object(request, object_id)
        self.slice_id = slice_id
        self.node_id = sliver.node_id
        context = {'title': mark_safe('Change sliver %s@%s' % \
                                      (admin_link('')(slice), admin_link('')(sliver.node))),
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
    readonly_fields = ['sliver_link', 'node_link', 'cn_url', 'sliver_note_hack',
                       'sliver_note_hack2']
    
    def sliver_note_hack(self, instance): pass
    sliver_note_hack.short_description = ('The slice must be registred before creating '
                                          'slivers. To do so select "Save and continue editing".')
    
    def sliver_note_hack2(self, instance): pass
    sliver_note_hack2.short_description = mark_safe('Use the <a href="add_sliver">'
                                                    '"Add Sliver"</a> button on the '
                                                    'top-left of this page')
    
    def get_fieldsets(self, request, obj=None):
        """ HACK display message using the field name of the inline form """
        if obj is None:
            return [(None, {'fields': ['sliver_note_hack']})]
        # The slices is registred, display add button as the inline header
        self.verbose_name_plural = mark_safe('Slivers <a href="add_sliver">(Add Sliver)</a>')
        if not obj.sliver_set.exists():
            return [(None, {'fields': ['sliver_note_hack2']})]
        return super(SliverInline, self).get_fieldsets(request, obj=obj)
    
    def has_delete_permission(self, request, obj=None):
        """ Do not display delete field when there is no slivers """
        if obj is None or not obj.sliver_set.exists():
            return False
        return super(SliverInline, self).has_delete_permission(request, obj=obj)
    
    def sliver_link(self, instance):
        url = reverse('admin:slices_slice_slivers', 
                      kwargs={'slice_id': instance.slice_id,
                              'object_id': instance.id})
        return mark_safe("<b><a href='%s'>%s</a></b>" % (url, instance))
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
    verbose_name_plural = mark_safe('Slice Properties %s' % docstring_as_help_tip(SliceProp))


class SliceAdmin(ChangeViewActionsModelAdmin, PermissionModelAdmin):
    list_display = ['name', 'vlan_nr', colored('set_state', STATE_COLORS, verbose=True),
                    num_slivers, admin_link('template'), 'expires_on', admin_link('group')]
    list_display_links = ('name',)
    list_filter = [MySlicesListFilter, 'set_state', 'template']
    readonly_fields = ['instance_sn', 'new_sliver_instance_sn', 'expires_on', 
                       'exp_data_sha256', template_link]
    date_hierarchy = 'expires_on'
    search_fields = ['name']
    inlines = [SlicePropInline, SliverInline]
    actions = [reset_selected, renew_selected_slices]
    form = SliceAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'description', ('template', template_link), ('exp_data', 
                       'exp_data_sha256'), 'set_state', 'vlan_nr', 
                       'instance_sn', 'new_sliver_instance_sn', 'expires_on',
                       'group'),
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
        qs = qs.annotate(models.Count('sliver', distinct=True))
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
                form.base_fields['group'].widget = ReadOnlyWidget(groups[0].id, groups[0].name)
                form.base_fields['group'].required = False
        return form
    
    def changelist_view(self, request, extra_context=None):
        """ Default filter as 'my_slices=True' """
        if not request.GET.has_key('my_slices'):
            q = request.GET.copy()
            q['my_slices'] = 'True'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(SliceAdmin, self).changelist_view(request, extra_context=extra_context)


class TemplateAdmin(PermissionModelAdmin):
    list_display = ['name', 'description', 'type', 'node_archs_str', 'image', 
                    'is_active']
    list_filter = ['is_active', 'type', 'node_archs']
    #FIXME node_archs: contains rather than exact
    search_fields = ['name', 'description', 'type', 'node_archs']
    fields = ['name', 'description', 'type', 'node_archs', 'image', 'image_sha256', 
              'is_active']
    readonly_fields = ['image_sha256']
    
    def image_sha256(self, instance):
        return instance.image_sha256
    image_sha256.short_description = 'Image SHA256'
    
    def node_archs_str(self, instance):
        return ', '.join(instance.node_archs)
    node_archs_str.short_description = 'Node archs'
    node_archs_str.admin_order_field = 'node_archs'


admin.site.register(Sliver, SliverAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Template, TemplateAdmin)


# Monkey-Patching Section

node_modeladmin = get_modeladmin(Node)
old_queryset = node_modeladmin.queryset

def queryset(request):
    " Annotate number of slivers for sorting on node changelist "
    qs = old_queryset(request)
    qs = qs.annotate(models.Count('sliver', distinct=True))
    return qs

node_modeladmin.queryset = queryset

insert_list_display(Node, num_slivers)
