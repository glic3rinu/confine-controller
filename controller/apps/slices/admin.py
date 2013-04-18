from __future__ import absolute_import

from django.conf.urls import patterns, url, include
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from controller.admin import ChangeViewActions, ChangeListDefaultFilter
from controller.admin.utils import (colored, admin_link, link, get_admin_link,
    insert_list_display, action_to_view, get_modeladmin, wrap_admin_view,
    docstring_as_help_tip)
from controller.forms.widgets import ReadOnlyWidget
from nodes.admin import NodeAdmin, STATES_COLORS
from nodes.models import Node
from permissions.admin import PermissionModelAdmin, PermissionTabularInline

from .actions import renew_selected_slices, reset_selected, update_selected, create_slivers
from .filters import MySlicesListFilter, MySliversListFilter
from .forms import SliceAdminForm, SliverIfaceInlineForm, SliverIfaceInlineFormSet
from .helpers import wrap_action, remove_slice_id
from .models import Sliver, SliverProp, SliverIface, Slice, SliceProp, Template


STATE_COLORS = { 
    Slice.REGISTER: 'grey',
    Slice.DEPLOY: 'darkorange',
    Slice.START: 'green' }


def num_slivers(instance):
    """ return num slivers as a link to slivers changelist view """
    num = instance.slivers.count()
    url = reverse('admin:slices_sliver_changelist')
    url += '?my_slivers=False&%s=%s' % (instance._meta.module_name, instance.pk)
    return mark_safe('<a href="%s">%d</a>' % (url, num))
num_slivers.short_description = 'Slivers'
num_slivers.admin_order_field = 'sliver__count'


def template_link(instance):
    """ Display template change view link """
    return get_admin_link(instance.template)


class SliverPropInline(PermissionTabularInline):
    model = SliverProp
    extra = 0
    verbose_name_plural = mark_safe('Sliver properties %s' % docstring_as_help_tip(SliverProp))


class SliverIfaceInline(PermissionTabularInline):
    model = SliverIface
    readonly_fields = ['nr', 'ipv6_addr', 'ipv4_addr']
    extra = 0
    formset = SliverIfaceInlineFormSet
    verbose_name_plural = mark_safe('Sliver network interfaces <a href="http://wiki.'
        'confine-project.eu/arch:node" onclick="return showAddAnotherPopup(this);">(Help)</a>')
    form = SliverIfaceInlineForm
    
    def get_formset(self, request, obj=None, **kwargs):
        """ Hook node for future usage in the inline form """
        self.form.node = request._node_
        self.form.slice = request._slice_
        return super(SliverIfaceInline, self).get_formset(request, obj=obj, **kwargs)


class SliverAdmin(ChangeViewActions, ChangeListDefaultFilter, PermissionModelAdmin):
    list_display = ['__unicode__', admin_link('node'), admin_link('slice')]
    list_filter = [MySliversListFilter, 'slice__name']
    fields = ['description', 'slice_link', 'node_link', 'instance_sn', 'template',
              template_link, 'exp_data', 'exp_data_uri', 'exp_data_sha256', 'set_state']
    readonly_fields = ['instance_sn', 'slice_link', 'node_link', template_link]
    search_fields = ['description', 'node__description', 'slice__name']
    inlines = [SliverIfaceInline]
    actions = [update_selected]
    change_view_actions = [update_selected]
    default_changelist_filter = 'my_slivers'
    change_form_template = "admin/controller/change_form.html"
    
    def __init__(self, *args, **kwargs):
        """ 
        For each sliver iface type show number of requested ifaces on sliver changelist
        """
        for iface_type, iface_object in Sliver.get_registered_ifaces().items():
            if not iface_type in self.list_display and not iface_object.AUTO_CREATE:
                def display_ifaces(instance, iface_type=iface_type):
                    return instance.interfaces.filter(type=iface_type).count()
                display_ifaces.short_description = iface_type.capitalize()
                display_ifaces.boolean = iface_object.UNIQUE
                setattr(self, iface_type, display_ifaces)
                self.list_display.append(iface_type)
        super(SliverAdmin, self).__init__(*args, **kwargs)
    
    def total_num_ifaces(self, instance):
        """ Total number of sliver ifaces used on list_display """
        return instance.interfaces.count()
    total_num_ifaces.short_description = 'Total Ifaces'
    total_num_ifaces.admin_order_field = 'interfaces__count'
    
    def slice_link(self, instance):
        """ Link to related slice used on change_view """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.slice))
    slice_link.short_description = 'Slice'
    
    def node_link(self, instance):
        """ Link to related node used on change_view """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.node))
    node_link.short_description = 'Node'
    
    def exp_data_sha256(self, instance):
        """ Experiment data SHA256 used on change_view """
        return instance.exp_data_sha256
    exp_data_sha256.short_description = 'Experiment Data SHA256'
    
    def has_add_permission(self, *args, **kwargs):
        """ 
        Remove add button on change list. Slivers can only be added from slice change form 
        """
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        """ Hook node reference for future processing in SliverIfaceInline """
        request._node_ = obj.node
        request._slice_ = obj.slice
        return super(SliverAdmin, self).get_form(request, obj, **kwargs)
    
    def queryset(self, request):
        """ Annotate number of ifaces for future ordering on the changellist """
        qs = super(SliverAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('interfaces', distinct=True))
        return qs
    
    def log_addition(self, request, object):
        """ AUTO_CREATE SliverIfaces """
        for iface_type, iface_object in Sliver.get_registered_ifaces().items():
            if iface_object.AUTO_CREATE and not object.interfaces.filter(type=iface_type).exists():
                SliverIface.objects.create(sliver=object, type=iface_type,
                    name=iface_object.DEFAULT_NAME)
        super(SliverAdmin, self).log_addition(request, object)


class NodeListAdmin(NodeAdmin):
    """ 
    Nested Node ModelAdmin that provides a list of available nodes for adding 
    slivers hooked on Slice
    """
    list_display = ['add_sliver_link', 'id', link('cn_url', description='CN URL'),
                    'arch', colored('set_state', STATES_COLORS, verbose=True),
                    admin_link('group'), 'num_ifaces', num_slivers, 
                    'display_sliver_pub_ipv4_range']
    list_display_links = ['add_sliver_link', 'id']
    # Template that fixes breadcrumbs for the new namespace
    change_list_template = 'admin/slices/slice/list_nodes.html'
    actions = [create_slivers]
    actions_on_bottom = True
    
    def add_sliver_link(self, instance):
        """ Link to add sliver to related node """
        kwargs = { 'slice_id':self.slice_id, 'node_id':instance.pk }
        url = reverse('admin:slices_slice_add_sliver', kwargs=kwargs)
        return '<a href="%s">%s<a>' % (url, instance.name)
    add_sliver_link.allow_tags = True
    add_sliver_link.short_description = 'Add on Node'
    
    def get_actions(self, request):
        """ Avoid inherit NodeAdmin actions """
        actions = super(NodeListAdmin, self).get_actions(request)
        return {'create_slivers': actions['create_slivers']}
    
    def display_sliver_pub_ipv4_range(self, instance):
        """ Show sliver_pub_ipv4_range on changeliste """
        return instance.sliver_pub_ipv4_range
    display_sliver_pub_ipv4_range.short_description = 'IPv4 Range'
    display_sliver_pub_ipv4_range.admin_order_field = 'sliver_pub_ipv4_range'
    
    def changelist_view(self, request, slice_id, extra_context=None):
        """ Just fixing title and breadcrumbs """
        self.slice_id = slice_id
        slice = Slice.objects.get(pk=slice_id)
        title = 'Select one or more nodes for creating %s slivers' % get_admin_link(slice)
        context = {'title': mark_safe(title),
                   'slice': slice, }
        context.update(extra_context or {})
        # call admin.ModelAdmin to avoid my_nodes default NodeAdmin changelist filter
        return admin.ModelAdmin.changelist_view(self, request, extra_context=context)
    
    def queryset(self, request):
        """ Filter node list excluding nodes with already slivers of the slice """
        qs = super(NodeListAdmin, self).queryset(request)
        qs = qs.exclude(slivers__slice=self.slice_id)
        qs = qs.annotate(models.Count('slivers'))
        return qs
    
    def has_add_permission(self, *args, **kwargs):
        """ Prevent node addition on this ModelAdmin """
        return False


class SliceSliversAdmin(SliverAdmin):
    """
    Nested Sliver ModelAdmin that provides Slivers management capabilities on Slices
    """
    fields = ['description', 'instance_sn', 'template', 'exp_data', 'exp_data_uri',
              'exp_data_sha256', 'set_state']
    add_form_template = 'admin/slices/slice/add_sliver.html'
    change_form_template = 'admin/slices/slice/change_sliver.html'
    readonly_fields = ['instance_sn']
    
    def add_view(self, request, slice_id, node_id, form_url='', extra_context=None):
        """ Customizations needed for being nested to slices """
        # hook for future use on self.save_model()
        self.slice_id = slice_id
        self.node_id = node_id
        slice = Slice.objects.get(pk=slice_id)
        node = Node.objects.get(pk=node_id)
        title = 'Add sliver %s@%s' % (get_admin_link(slice), get_admin_link(node))
        context = {'title': mark_safe(title),
                   'slice': slice,}
        context.update(extra_context or {})
        return super(SliceSliversAdmin, self).add_view(request, form_url='', extra_context=context)
    
    def change_view(self, request, object_id, slice_id, form_url='', extra_context=None):
        """ Customizations needed for being nested to slices """
        slice = Slice.objects.get(pk=slice_id)
        self.slice_id = slice_id
        sliver = self.get_object(request, object_id)
        self.node_id = sliver.node_id
        context = { 'slice': slice }
        context.update(extra_context or {})
        return super(SliceSliversAdmin, self).change_view(request, object_id,
            form_url=form_url, extra_context=context)
    
    def save_model(self, request, obj, *args, **kwargs):
        """ Provde node and slice attributes to obj sliver """
        obj.node = Node.objects.get(pk=self.node_id)
        slice = Slice.objects.get(pk=self.slice_id)
        obj.slice = slice
        super(SliceSliversAdmin, self).save_model(request, obj, *args, **kwargs)
        slice_modeladmin = SliceAdmin(slice, self.admin_site)
        slice_modeladmin.log_change(request, slice, 'Added sliver "%s"' % obj)
    
    def response_add(self, request, obj, post_url_continue=None):
        """ Customizations needed for being nested to slices """
        post_url_continue = reverse('admin:slices_slice_slivers', args=(obj.slice.pk, obj.pk))
        response = super(SliceSliversAdmin, self).response_add(request, obj,
            post_url_continue=post_url_continue)
        # save and continue correction
        if response._headers.get('location')[1] == request.path:
            return HttpResponseRedirect(reverse('admin:slices_slice_add_sliver', args=(obj.slice.pk,)))
        return response
    
    def response_change(self, request, obj):
        """ Customizations needed for being nested to slices """
        response = super(SliceSliversAdmin, self).response_change(request, obj)
        # save and add another correction
        if response._headers.get('location')[1] == reverse('admin:slices_sliver_add'):
            return HttpResponseRedirect(reverse('admin:slices_slice_add_sliver', args=(obj.slice.pk,)))
        return response
    
    def has_add_permission(self, *args, **kwargs):
        """ Skip SliverAdmin.has_add_permission definition """
        return super(SliverAdmin, self).has_add_permission(*args, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        """ Hook node reference for future processing in IsolatedIfaceInline """
        if obj: 
            request._node_ = obj.node
            request._slice_ = obj.slice
        else:
            # TODO gatting node_id/slice_id like this is really embarassing...
            node_id = request.path.split('/')[-2]
            node = Node.objects.get(pk=node_id)
            request._node_ = node
            slice_id = request.path.split('/')[-4]
            slice = Slice.objects.get(pk=slice_id)
            request._slice_ = slice
        return super(SliverAdmin, self).get_form(request, obj, **kwargs)


class SliverInline(PermissionTabularInline):
    """ Show slivers in read only fashion """
    model = Sliver
    max_num = 0
    fields = ['sliver_link', 'node_link', 'cn_url']
    readonly_fields = ['sliver_link', 'node_link', 'cn_url', 'sliver_note1',
                       'sliver_note2']
    
    def sliver_note1(self, instance):
        """
        <p>The slice must be saved before creating slivers.
        <input type="submit" value="Save" name="_continue" /></p>
        """
    sliver_note1.short_description = mark_safe(sliver_note1.__doc__)
    
    def sliver_note2(self, instance):
        """
        <a href="add_sliver" class="addlink"> Add Slivers </a>
        """
    sliver_note2.short_description = mark_safe(sliver_note2.__doc__)
    
    def get_fieldsets(self, request, obj=None):
        """ HACK display message using the field name of the inline form """
        if obj is None:
            return [(None, {'fields': ['sliver_note1']})]
        # The slices is registred: display add button in the inline header
        if self.has_change_permission(request, obj, view=False):
            self.verbose_name_plural = mark_safe('Slivers <a href="add_sliver">'
                                                 '(Add another Sliver)</a>')
        if not obj.slivers.exists():
            return [(None, {'fields': ['sliver_note2']})]
    
        return super(SliverInline, self).get_fieldsets(request, obj=obj)
    
    def has_delete_permission(self, request, obj=None):
        """ Do not display delete field when there is no slivers """
        if obj is None or not obj.slivers.exists():
            return False
        return super(SliverInline, self).has_delete_permission(request, obj=obj)
    
    def sliver_link(self, instance):
        """ Display sliver change link on the inline form """
        kwargs = {'slice_id': instance.slice_id,
                  'object_id': instance.id}
        url = reverse('admin:slices_slice_slivers', kwargs=kwargs)
        return mark_safe("<b><a href='%s'>%s</a></b>" % (url, instance))
    sliver_link.short_description = 'Sliver'
    
    def node_link(self, instance):
        """ Display node change link on the inline form """
        return get_admin_link(instance.node)
    node_link.short_description = 'Node'
    
    def cn_url(self, instance):
        """ Display CN url on the inline form """
        node = instance.node
        return mark_safe("<a href='%s'>%s</a>" % (node.cn_url, node.cn_url))


class SlicePropInline(PermissionTabularInline):
    model = SliceProp
    extra = 0
    verbose_name_plural = mark_safe('Slice Properties %s' % docstring_as_help_tip(SliceProp))


class SliceAdmin(ChangeViewActions, ChangeListDefaultFilter, PermissionModelAdmin):
    list_display = ['name', 'id', 'vlan_nr', colored('set_state', STATE_COLORS, verbose=True),
                    num_slivers, admin_link('template'), 'expires_on', admin_link('group')]
    list_display_links = ('name', 'id')
    list_filter = [MySlicesListFilter, 'set_state', 'template']
    readonly_fields = ['instance_sn', 'new_sliver_instance_sn', 'expires_on', template_link]
    date_hierarchy = 'expires_on'
    search_fields = ['name']
    inlines = [SliverInline]
    actions = [reset_selected, renew_selected_slices]
    form = SliceAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'description', ('template', template_link),
                       ('exp_data', 'exp_data_uri'), 'exp_data_sha256', 'set_state',
                       'vlan_nr', 'expires_on', 'group'),
        }),
        ('Debug info', {
            'classes': ('collapse',),
            'fields': ('instance_sn', 'new_sliver_instance_sn',)
        }),)
    change_form_template = "admin/slices/slice/change_form.html"
    save_and_continue = True
    change_view_actions = [renew_selected_slices, reset_selected]
    default_changelist_filter = 'my_slices'
    
    def exp_data_sha256(self, instance):
        return instance.exp_data_sha256
    exp_data_sha256.short_description = 'Experiment Data SHA256'
    
    def queryset(self, request):
        """ Annotate number of slivers on the slice for sorting on changelist """
        qs = super(SliceAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('slivers', distinct=True))
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
            url("^(?P<slice_id>\d+)/slivers/(?P<object_id>\d+)/update",
                wrap_admin_view(self, wrap_action(update_selected,
                    SliceSliversAdmin(Sliver, admin_site))),)
        )
        return extra_urls + urls
    
    def get_form(self, request, *args, **kwargs):
        """ 
        Request.user as default node admin and Warn the user that the testbed is 
        not ready for allocating shit
        """
        if request.method == 'GET':
            messages.warning(request, 'At this time the testbed is not ready for '
                'allocating slices. But you are welcome to try this interface anyway.')
        form = super(SliceAdmin, self).get_form(request, *args, **kwargs)
        if 'group' in form.base_fields:
            # ronly forms doesn't have initial nor queryset
            user = request.user
            groups = user.groups.filter(Q(roles__is_admin=True) | Q(roles__is_researcher=True))
            groups = groups.filter(allow_slices=True)
            num_groups = groups.count()
            if num_groups >= 1:
                form.base_fields['group'].queryset = groups
            if num_groups == 1:
                form.base_fields['group'].widget = ReadOnlyWidget(groups[0].id, groups[0].name)
                form.base_fields['group'].required = False
        return form
    
    def get_readonly_fields(self, request, obj=None):
        """ Disable set_state transitions when slice is registered """
        readonly_fields = super(SliceAdmin, self).get_readonly_fields(request, obj=obj)
        if 'set_state' not in readonly_fields and obj is None:
            return readonly_fields + ['set_state']
        return readonly_fields


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
    """ Annotate number of slivers for sorting on node changelist """
    qs = old_queryset(request)
    qs = qs.annotate(models.Count('slivers', distinct=True))
    return qs

node_modeladmin.queryset = queryset

insert_list_display(Node, num_slivers)
