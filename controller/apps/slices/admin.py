from __future__ import absolute_import

from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe

from controller.admin import ChangeViewActions, ChangeListDefaultFilter
from controller.admin.utils import (colored, admin_link, link, get_admin_link,
    insertattr, get_modeladmin, wrap_admin_view, docstring_as_help_tip)
from controller.admin.widgets import LinkedRelatedFieldWidgetWrapper
from controller.core.exceptions import DisallowedSliverCreation
from nodes.admin import NodeAdmin
from nodes.models import Node
from permissions.admin import (PermissionModelAdmin, PermissionStackedInline,
    PermissionTabularInline)
from users.helpers import filter_group_queryset

from .actions import renew_selected_slices, reset_selected, update_selected, create_slivers
from .filters import MySlicesListFilter, MySliversListFilter, SliverSetStateListFilter
from .forms import (SliverDefaultsInlineForm, SliverAdminForm, SliverIfaceInlineForm,
    SliverIfaceInlineFormSet, SliceSliversForm)
from .helpers import (get_readonly_file_fields, is_valid_description,
    log_sliver_history, remove_slice_id, state_value, wrap_action)
from .models import (Slice, SliceProp, Sliver, SliverDefaults, SliverProp,
    SliverIface, Template)


# List of ifaces displayed in SliverInline (and subclasses)
SLIVER_IFACES = ['public6', 'public4', 'management', 'isolated', 'debug']

STATE_COLORS = {
    Slice.REGISTER: 'grey',
    Slice.DEPLOY: 'darkorange',
    Slice.START: 'green'
}


colored_set_state = colored('set_state', STATE_COLORS, verbose=True, bold=False)

def num_slivers(instance):
    """ return num slivers as a link to slivers changelist view """
    num = instance.slivers.count()
    url = reverse('admin:slices_sliver_changelist')
    url += '?my_slivers=False&%s=%s' % (instance._meta.model_name, instance.pk)
    return mark_safe('<a href="%s">%d</a>' % (url, num))
num_slivers.short_description = 'Slivers'
num_slivers.admin_order_field = 'slivers__count'


def computed_sliver_set_state(sliver):
    title = ''

    # compute if state is overridden...
    is_state_overridden = False
    state = sliver.effective_set_state
    sliver_state = sliver.set_state or sliver.slice.sliver_defaults.set_state
    # ...by slice
    if state != sliver_state and (state == Slice.REGISTER or sliver_state == Slice.START):
        is_state_overridden = True
        sliver_state_name = filter(lambda s: s[0] == sliver_state, Slice.STATES)[0][1]
        title = 'Set state from slice, sliver set state is %s' % sliver_state_name
    # ...by sliver defaults
    if sliver.set_state is None:
        is_state_overridden = True
        if not title:
            title = 'Set state from sliver defaults, sliver has no set state'
        else:  # already overridden by slice
            title += ' (from sliver defaults)'

    # init state representation
    color = STATE_COLORS.get(state, "black")
    state_name = filter(lambda s: s[0] == state, Slice.STATES)[0][1]
    if is_state_overridden:
        state_name += '*'
    
    return mark_safe('<span style="color:%s;" title="%s">%s</span>' % (color, title, state_name))
computed_sliver_set_state.short_description = 'Set state'


class SliverPropInline(PermissionTabularInline):
    model = SliverProp
    extra = 1
    verbose_name_plural = mark_safe('Sliver properties %s' % docstring_as_help_tip(SliverProp))
    
    class Media:
        js = ('slices/js/collapsed_properties.js',)


class SliverIfaceInline(PermissionTabularInline):
    model = SliverIface
    readonly_fields = ['nr', 'ipv6_addr', 'ipv4_addr']
    extra = 0
    formset = SliverIfaceInlineFormSet
    verbose_name_plural = mark_safe('Sliver network interfaces <a href="http://wiki.'
        'confine-project.eu/arch:node" onclick="return showAddAnotherPopup(this);">(Help)</a>')
    form = SliverIfaceInlineForm
    
    class Media:
        css = {
             'all': (
                'controller/css/hide-inline-id.css',)
        }
    
    def get_formset(self, request, obj=None, **kwargs):
        """ Hook node for future usage in the inline form """
        self.form.node = request._node_
        self.form.slice = request._slice_
        return super(SliverIfaceInline, self).get_formset(request, obj=obj, **kwargs)


SLIVER_EMPTY_LABEL = "(from slice's sliver defaults)"
class SliverAdmin(ChangeViewActions, ChangeListDefaultFilter, PermissionModelAdmin):
    list_display = [
        '__unicode__', admin_link('node'), admin_link('slice'), computed_sliver_set_state
    ]
    list_filter = [MySliversListFilter, SliverSetStateListFilter, 'slice', 'slice__group']
    fieldsets = (
        (None, {
            'fields': ('description', 'template', 'set_state')
        }),
        ('Advanced', {
            'classes': ('collapse', 'info'),
            'description': 'If you want to define a URI, you should remove '
                           'previously the uploaded file.',
            'fields': ('data', 'data_uri', 'data_sha256',
                       'new_instance_sn')
        }),
    )
    readonly_fields = ['new_instance_sn']
    search_fields = ['description', 'node__description', 'node__name', 'slice__name']
    inlines = [SliverPropInline, SliverIfaceInline]
    actions = [update_selected]
    change_view_actions = [update_selected]
    default_changelist_filters = (('my_slivers', 'True'),)
    change_form_template = "admin/controller/change_form.html"
    form = SliverAdminForm
    
    class Media:
        css = {
             'all': (
                'slices/css/warning-form.css',)
        }
    
    def __init__(self, *args, **kwargs):
        """ 
        For each sliver iface type show number of requested ifaces on sliver changelist
        """
        for iface_type, iface_object in Sliver.get_registered_ifaces().items():
            """ Hook registered ifaces """
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
    total_num_ifaces.short_description = 'Total ifaces'
    total_num_ifaces.admin_order_field = 'interfaces__count'
    
    def new_instance_sn(self, instance):
        if instance.pk:
            return instance.instance_sn
        return instance.slice.sliver_defaults.instance_sn
    new_instance_sn.short_description ='Instance sequence number'
    
    def has_add_permission(self, *args, **kwargs):
        """ 
        Removes add button on change list. Slivers can only be added from slice change form 
        """
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        """ Hook node reference for future processing in SliverIfaceInline """
        request._node_ = obj.node
        request._slice_ = obj.slice
        return super(SliverAdmin, self).get_form(request, obj, **kwargs)
    
    def get_readonly_fields(self, request, obj=None):
        """Mark as readonly if exists file for data."""
        readonly_fields = super(SliverAdmin, self).get_readonly_fields(request, obj=obj)
        return readonly_fields + get_readonly_file_fields(obj)
    
    def get_queryset(self, request):
        """ Annotate number of ifaces for future ordering on the changelist """
        related = ('node', 'slice')
        qs = super(SliverAdmin, self).get_queryset(request).select_related(*related)
        qs = qs.annotate(models.Count('interfaces', distinct=True))
        return qs
    
    def log_addition(self, request, object):
        """ AUTO_CREATE SliverIfaces """
        for iface_type, iface_object in Sliver.get_registered_ifaces().items():
            if (iface_object.AUTO_CREATE and
                not object.interfaces.filter(type=iface_type).exists()):
                    SliverIface.objects.create(sliver=object, type=iface_type,
                                               name=iface_object.DEFAULT_NAME)
        super(SliverAdmin, self).log_addition(request, object)
        # log sliver history on the node #523
        msg = 'Added sliver "%s" (%i).' % (object, object.pk)
        log_sliver_history(request.user.pk, object, msg)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make description input widget smaller and update empty label """
        if db_field.name == 'description':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 85, 'rows': 5})
        elif db_field.name == 'template':
            kwargs['empty_label'] = SLIVER_EMPTY_LABEL
            formfield = self.formfield_for_foreignkey(db_field, **kwargs)
            kwargs['widget'] = LinkedRelatedFieldWidgetWrapper(formfield.widget,
                    db_field.rel, self.admin_site)
        elif  '_sha256' in db_field.name or '_uri' in db_field.name:
            kwargs['widget'] = forms.TextInput(attrs={'size': 80})
        return super(SliverAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """ Update empty label """
        if db_field.name == 'set_state':
            blank_choice = (('', SLIVER_EMPTY_LABEL),)
            kwargs['choices'] = blank_choice + Slice.STATES
        # TODO update empty_label for sliver data (FileField)
        return super(SliverAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Linked title """
        # Check object_id is a valid pk (simplification of ModelAdmin.get_object)
        try:
            int(object_id)
        except ValueError:
            object_id = None
        obj = get_object_or_404(Sliver, pk=object_id)
        slice_link = get_admin_link(obj.slice)
        node_link = get_admin_link(obj.node)
        context = {
            'title': mark_safe('Change sliver %s@%s' % (slice_link, node_link)),
            'header_title': 'Change sliver'
        }
        context.update(extra_context or {})
        
        if request.method == 'GET':
            # notify user about relevant sliver config
            sliver_state = obj.set_state
            slice_state = obj.slice.set_state
            if state_value(sliver_state) > state_value(slice_state):
                msg = ("Note: the slice's set state '%s' overrides the "
                       "sliver's current set state '%s'.") % (slice_state,
                        sliver_state)
                messages.warning(request, msg)
            
            if (not is_valid_description(obj.slice.description) and
                not is_valid_description(obj.description)):
                msg = ("The sliver description is too short. Please provide "
                       "more details about the experiment or service. Help us "
                       "providing valuable feedback to Community Networks' "
                       "members.")
                messages.warning(request, msg)
        
        return super(SliverAdmin, self).change_view(request, object_id,
                form_url=form_url, extra_context=context)
    
    def log_change(self, request, object, message):
        super(SliverAdmin, self).log_change(request, object, message)
        # log sliver history on the node #523
        if 'set_state' in message:
            msg = ('Changed set_state to "%s" of sliver "%s" (%i). NOTE: set '
                  'state may differ from effective set state.' %
                   (object.set_state, object, object.pk))
            log_sliver_history(request.user.pk, object, msg)


class NodeListAdmin(NodeAdmin):
    """ 
    Nested Node ModelAdmin that provides a list of available nodes for adding 
    slivers hooked on Slice
    """
    list_display = [
        'add_sliver_link', 'id', 'arch', 'display_set_state',
        admin_link('group'), 'num_ifaces', num_slivers,
        'display_sliver_pub_ipv4_range'
    ]
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
    add_sliver_link.short_description = 'Add on node'
    
    def display_sliver_pub_ipv4_range(self, instance):
        """ Show sliver_pub_ipv4_range on changelist """
        return instance.sliver_pub_ipv4_range
    display_sliver_pub_ipv4_range.short_description = 'IPv4 Range'
    display_sliver_pub_ipv4_range.admin_order_field = 'sliver_pub_ipv4_range'
    
    def get_actions(self, request):
        """ Avoid inherit NodeAdmin actions """
        actions = super(NodeListAdmin, self).get_actions(request)
        return { 'create_slivers': actions['create_slivers'] }
    
    def get_queryset(self, request):
        """ Filter node list excluding nodes with already slivers of the slice """
        qs = super(NodeListAdmin, self).get_queryset(request)
        qs = qs.exclude(slivers__slice=self.slice_id)
        qs = qs.annotate(models.Count('slivers'))
        return qs
    
    def has_change_permission(self, request, obj=None, view=True):
        """ Inherit permissions from SliceModelAdmin """
        slice_modeladmin = get_modeladmin(Slice)
        return slice_modeladmin.has_change_permission(request, obj=obj, view=view)
    
    def has_add_permission(self, *args, **kwargs):
        """ Prevent node addition on this ModelAdmin """
        return False
    
    def changelist_view(self, request, slice_id, extra_context=None):
        """ Just fixing title and breadcrumbs """
        slice = get_object_or_404(Slice, pk=slice_id)
        self.slice_id = slice_id
        title = 'Select one or more nodes for creating %s slivers' % get_admin_link(slice)
        context = {
            'title': mark_safe(title),
            'slice': slice,
        }
        context.update(extra_context or {})
        # call admin.ModelAdmin to avoid my_nodes default NodeAdmin changelist filter
        return admin.ModelAdmin.changelist_view(self, request, extra_context=context)


class SliceSliversAdmin(SliverAdmin):
    """
    Nested Sliver ModelAdmin that provides Slivers management capabilities on Slices
    """
    add_form_template = 'admin/slices/slice/add_sliver.html'
    change_form_template = 'admin/slices/slice/change_sliver.html'
    form = SliceSliversForm
    
    def slice_link(self, instance):
        """ Link to related slice used on change_view """
        if not instance.slice_id:
            instance.slice_id = self.slice_id
        return super(SliceSliversAdmin, self).slice_link(instance)
    slice_link.short_description = 'Slice'
    
    def node_link(self, instance):
        """ Link to related node used on change_view """
        if not instance.node_id:
            instance.node_id = self.node_id
        return super(SliceSliversAdmin, self).node_link(instance)
    node_link.short_description = 'Node'
    
    def get_form(self, request, obj=None, **kwargs):
        """ Hook node reference for future processing in IsolatedIfaceInline """
        form = super(SliverAdmin, self).get_form(request, obj, **kwargs)
        if obj: 
            form.node = obj.node
            form.slice = obj.slice
        else:
            form.node = get_object_or_404(Node, pk=self.node_id)
            form.slice = get_object_or_404(Slice, pk=self.slice_id)
        request._slice_ = form.slice
        request._node_ = form.node
        return form
    
    def save_model(self, request, obj, *args, **kwargs):
        """ Provide node and slice attributes to obj sliver """
        obj.node = get_object_or_404(Node, pk=self.node_id)
        slice = get_object_or_404(Slice, pk=self.slice_id)
        obj.slice = slice
        super(SliceSliversAdmin, self).save_model(request, obj, *args, **kwargs)
        slice_modeladmin = SliceAdmin(slice, self.admin_site)
        slice_modeladmin.log_change(request, slice, 'Added sliver "%s"' % obj)
    
    def has_add_permission(self, *args, **kwargs):
        """ Skip SliverAdmin.has_add_permission definition """
        return super(SliverAdmin, self).has_add_permission(*args, **kwargs)
    
    def response_add(self, request, obj, post_url_continue=None):
        """ Customizations needed for being nested to slices """
        # "save and continue" correction
        args = (obj.slice.pk, obj.pk)
        post_url_continue = reverse('admin:slices_slice_slivers', args=args)
        response = super(SliceSliversAdmin, self).response_add(request, obj,
                post_url_continue=post_url_continue)
        # "save and continue" correction
        location = response._headers.get('location')[1]
        if  location == request.path:
            url = reverse('admin:slices_slice_add_sliver', args=(obj.slice.pk,))
            return HttpResponseRedirect(url)
        # "save" correction
        if location == reverse('admin:slices_sliver_changelist'):
            url = reverse('admin:slices_slice_change', args=(obj.slice.pk,))
            return HttpResponseRedirect(url)
        return response
    
    def response_change(self, request, obj):
        """ Customizations needed for being nested to slices """
        response = super(SliceSliversAdmin, self).response_change(request, obj)
        location = response._headers.get('location')[1]
        # "save and add another" correction
        if location == reverse('admin:slices_sliver_add'):
            url = reverse('admin:slices_slice_add_sliver', args=(obj.slice.pk,))
            return HttpResponseRedirect(url)
        # "save" correction
        if location == reverse('admin:slices_sliver_changelist'):
            url = reverse('admin:slices_slice_change', args=(obj.slice.pk,))
            return HttpResponseRedirect(url)
        return response
    
    def add_view(self, request, slice_id, node_id, form_url='', extra_context=None):
        """ Customizations needed for being nested to slices """
        # hook for future use on self.save_model()
        slice = get_object_or_404(Slice, pk=slice_id)
        node = get_object_or_404(Node, pk=node_id)
        if Sliver.objects.filter(node=node, slice=slice).exists():
            raise DisallowedSliverCreation()
        self.slice_id = slice_id
        self.node_id = node_id
        title = 'Add sliver %s@%s' % (get_admin_link(slice), get_admin_link(node))
        context = {
            'header_title': 'Add sliver',
            'title': mark_safe(title),
            'slice': slice,
        }
        context.update(extra_context or {})
        return super(SliceSliversAdmin, self).add_view(request, form_url='',
                extra_context=context)
    
    def change_view(self, request, object_id, slice_id, form_url='', extra_context=None):
        """ Customizations needed for being nested to slices """
        slice = get_object_or_404(Slice, pk=slice_id)
        sliver = get_object_or_404(Sliver, pk=object_id, slice=slice)
        self.slice_id = slice_id
        self.node_id = sliver.node_id
        context = { 'slice': slice }
        context.update(extra_context or {})
        # warn user on missconfiguration
        if request.method == 'GET':
            if not slice.sliver_defaults.template.is_active or \
                sliver.template and not sliver.template.is_active:
                msg = "The template chosen for this sliver is NOT active. "\
                    "Please check its configuration."
                messages.warning(request, msg)
        return super(SliceSliversAdmin, self).change_view(request, object_id,
                form_url=form_url, extra_context=context)


class SliverInline(PermissionTabularInline):
    """ Show slivers in read only fashion """
    model = Sliver
    max_num = 0
    fields = ['sliver_link', 'node_link', computed_sliver_set_state] + SLIVER_IFACES
    ordering = ['node__name']
    readonly_fields = [
        'sliver_link', 'node_link', computed_sliver_set_state, 'sliver_note1',
        'sliver_note2'
    ] + SLIVER_IFACES
    
    class Media:
        css = {
             'all': (
                'controller/css/hide-inline-id.css',)
        }
    
    def public6(self, instance):
        return instance.interfaces.filter(type='public6').count()
    
    def public4(self, instance):
        return instance.interfaces.filter(type='public4').count()
    
    def management(self, instance):
        return instance.interfaces.filter(type='management').exists()
    management.boolean = True
    
    def isolated(self, instance):
        return instance.interfaces.filter(type='isolated').count()
    
    def debug(self, instance):
        return instance.interfaces.filter(type='debug').count()
    
    def sliver_note1(self, instance):
        """
        <p>This slice must be saved before creating slivers.
        <input type="submit" value="Save" name="_continue" /></p>
        """
    sliver_note1.short_description = mark_safe(sliver_note1.__doc__)
    
    def sliver_note2(self, instance):
        """ <a href="add_sliver" class="addlink">Add slivers</a> """
    sliver_note2.short_description = mark_safe(sliver_note2.__doc__)
    
    def get_fieldsets(self, request, obj=None):
        """ HACK display message using the field name of the inline form """
        if obj is None:
            return [(None, {'fields': ['sliver_note1']})]
        # The slices is registered: display add button in the inline header
        if self.has_change_permission(request, obj, view=False):
            add_button = 'Slivers <a href="add_sliver">(Add another sliver)</a>'
            self.verbose_name_plural = mark_safe(add_button)
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
        if not instance.pk:
            return
        kwargs = {
            'slice_id': instance.slice_id,
            'object_id': instance.id}
        url = reverse('admin:slices_slice_slivers', kwargs=kwargs)
        return mark_safe("<b><a href='%s'>%s</a></b>" % (url, instance))
    sliver_link.short_description = 'Sliver'
    
    def node_link(self, instance):
        """ Display node change link on the inline form """
        return get_admin_link(instance.node)
    node_link.short_description = 'Node'


class SliverNodeInline(SliverInline):
    fields = ['sliver_link', 'slice_link', computed_sliver_set_state] + SLIVER_IFACES
    readonly_fields = ['sliver_link', 'slice_link', computed_sliver_set_state] + SLIVER_IFACES
    
    class Media:
        js = ('slices/js/collapsed_sliver_inline.js',)
    
    def get_fieldsets(self, request, obj=None):
        return super(SliverInline, self).get_fieldsets(request, obj=obj)
    
    def has_delete_permission(self, request, obj=None):
        """
        Disallow deleting slivers from node change_view:
        Why a node admin will be able to do that?
        """
        return False
    
    def has_change_permission(self, request, obj=None, view=False):
        # HACK for allow node_admins change a node with slivers
        # As this Inline is readonly and doesn't allow to introduce
        # changes, this workaround shouldn't have side effects
        # See #476
        return True

    def slice_link(self, instance):
        return get_admin_link(instance.slice)
    slice_link.short_description = 'Slice'


class SlicePropInline(PermissionTabularInline):
    model = SliceProp
    extra = 1
    verbose_name_plural = mark_safe('Slice properties %s' % docstring_as_help_tip(SliceProp))
    
    class Media:
        js = ('slices/js/collapsed_properties.js',)


class SliverDefaultsInline(PermissionStackedInline):
    model = SliverDefaults
    fieldsets = (
        (None, {
            'classes': ('info',),
            'description': 'If you want to define a URI, you should remove '
                           'previously the uploaded file.',
            'fields': ('template', 'set_state','data', 'data_uri', 'data_sha256',
                       'instance_sn')
        }),
    )
    readonly_fields = ['instance_sn']
    form = SliverDefaultsInlineForm
    can_delete = False
    
    class Media:
        css = {
             'all': (
                'slices/css/warning-form.css',)
        }

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'template':
            formfield = self.formfield_for_foreignkey(db_field, **kwargs)
            kwargs['widget'] = LinkedRelatedFieldWidgetWrapper(formfield.widget,
                db_field.rel, self.admin_site)
        elif  '_sha256' in db_field.name or '_uri' in db_field.name:
            kwargs['widget'] = forms.TextInput(attrs={'size': 80})
        return super(SliverDefaultsInline, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_readonly_fields(self, request, obj=None):
        """Mark as readonly if exists file for data."""
        readonly_fields = super(SliverDefaultsInline, self).get_readonly_fields(request, obj=obj)
        if obj is None:
            return readonly_fields
        return readonly_fields + get_readonly_file_fields(obj.sliver_defaults)


class SliceAdmin(ChangeViewActions, ChangeListDefaultFilter, PermissionModelAdmin):
    list_display = [
        'name', 'id', 'isolated_vlan_tag', colored_set_state, num_slivers,
        'display_template', 'expires_on', admin_link('group')
    ]
    list_display_links = ('name', 'id')
    list_filter = [MySlicesListFilter, 'set_state', 'group', 'sliver_defaults__template']
    readonly_fields = ['instance_sn', 'expires_on', 'isolated_vlan_tag']
    date_hierarchy = 'expires_on'
    search_fields = ['name']
    inlines = [SlicePropInline, SliverDefaultsInline, SliverInline]
    actions = [reset_selected, renew_selected_slices]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'set_state', 'expires_on', 'group'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('allow_isolated', 'isolated_vlan_tag', 'instance_sn')
        }),
    )
    change_form_template = "admin/slices/slice/change_form.html"
    save_and_continue = True
    change_view_actions = [renew_selected_slices, reset_selected]
    default_changelist_filters = (('my_slices', 'True'),)

    class Media:
        css = {
            "all" : ("slices/css/hide_admin_obj_name.css",)
        }
    
    def get_queryset(self, request):
        """ Annotate number of slivers on the slice for sorting on changelist """
        related = ('group', 'template')
        qs = super(SliceAdmin, self).get_queryset(request).select_related(*related)
        qs = qs.annotate(models.Count('slivers', distinct=True))
        return qs
    
    def get_urls(self):
        """ Hook sliver management URLs on slice admin """
        urls = super(SliceAdmin, self).get_urls()
        admin_site = self.admin_site
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
    
    def get_form(self, request, obj=None, *args, **kwargs):
        """ 
        Request.user as default node admin and Warn the user that the testbed is
        not ready for allocating shit
        """
        form = super(SliceAdmin, self).get_form(request, obj=obj, *args, **kwargs)
        if 'group' in form.base_fields:
            # ronly forms doesn't have initial nor queryset
            query = Q( Q(users__roles__is_group_admin=True) | Q(users__roles__is_slice_admin=True) )
            query = Q( query & Q(allow_slices=True) )
            form = filter_group_queryset(form, obj, request.user, query)
        return form
    
    def get_readonly_fields(self, request, obj=None):
        """ Disable set_state transitions on slice creation.
            allow_isolated can be only updated on REGISTER state
        """
        readonly_fields = super(SliceAdmin, self).get_readonly_fields(request, obj=obj)
        if obj is None:
            if 'set_state' not in readonly_fields:
                return readonly_fields + ['set_state']
        elif obj.set_state != Slice.REGISTER:
            return readonly_fields + ['allow_isolated']
        return readonly_fields
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make description input widget smaller """
        if db_field.name == 'description':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 85, 'rows': 5})
        return super(SliceAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Warn user on:
            1. Missconfigured slice:
                a) Slice's group cannot manage slices
                b) Slice's sliver defaults template is inactive
            2. Too little information on the slice's description
        """
        if request.method == 'GET':
            obj = self.get_object(request, object_id)
            if obj and not obj.group.allow_slices:
                msg = "The slice group does not have permissions to manage slices"
                messages.warning(request, msg)
            if obj and not obj.sliver_defaults.template.is_active:
                msg = "The template chosen for this slice is NOT active. "\
                    "Please check its configuration."
                messages.warning(request, msg)
            if obj and not is_valid_description(obj.description):
                msg = ("The slice description is too short. Please provide "
                       "more details about the experiment or service. Help us "
                       "providing valuable feedback to Community Networks' "
                       "members.")
                messages.warning(request, msg)
        return super(SliceAdmin, self).change_view(request, object_id,
                form_url=form_url, extra_context=extra_context)
    
    def display_template(self, obj):
        """ Show SliverDefaults template on Slice changelist"""
        return get_admin_link(obj.sliver_defaults.template)
    display_template.short_description = 'template'


class TemplateAdmin(PermissionModelAdmin):
    list_display = [
        'name', 'description', 'type', 'node_archs_str', 'image', 'is_active'
    ]
    list_filter = ['is_active', 'type', 'node_archs']
    search_fields = ['name', 'description', 'type', '=node_archs', '^node_archs']
    fields = [
        'name', 'description', 'type', 'node_archs', 'image', 'image_sha256', 'is_active'
    ]
    readonly_fields = ['image_sha256']
    
    def node_archs_str(self, instance):
        return ', '.join(instance.node_archs)
    node_archs_str.short_description = 'Node archs'
    node_archs_str.admin_order_field = 'node_archs'
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make description input widget smaller """
        if db_field.name == 'description':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 85, 'rows': 5})
        return super(TemplateAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(Sliver, SliverAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Template, TemplateAdmin)


# Monkey-Patching Section

insertattr(Node, 'list_display', num_slivers)
insertattr(Node, 'inlines', SliverNodeInline, weight=5)
