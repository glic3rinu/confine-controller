from common.admin import ChangeViewActionsMixin, colored, admin_link
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from nodes.models import Node
from slices.actions import renew_selected_slices, reset_selected
from slices.forms import SliverInlineAdminForm
from slices.models import (Sliver, SliverProp, IsolatedIface, PublicIface, 
    PrivateIface, Slice, SliceProp, Template)


STATE_COLORS = { 'register': 'grey',
                 'instantiate': 'darkorange',
                 'activate': 'green' }


class SliverPropInline(admin.TabularInline):
    model = SliverProp
    extra = 0


class IsolatedIfaceInline(admin.TabularInline):
    model = IsolatedIface
    extra = 0


class PublicIfaceInline(admin.TabularInline):
    model = PublicIface
    extra = 0


class PrivateIfaceInline(admin.TabularInline):
    model = PrivateIface
    extra = 0


class SliverAdmin(ChangeViewActionsMixin):
    list_display = ['id', 'description', 'instance_sn', admin_link('node'), admin_link('slice')]
    list_filter = ['slice__name']
    readonly_fields = ['instance_sn']
    search_fields = ['description', 'node__description', 'slice__name']
    inlines = [SliverPropInline, IsolatedIfaceInline, PublicIfaceInline, 
               PrivateIfaceInline]
    actions = [reset_selected]
    change_view_actions = [('reset', reset_selected, '', ''),]


def add_sliver_link(self):
    return '<a href="%s">%s</a>' % (self.id, self.description)
add_sliver_link.short_description = 'Node'
add_sliver_link.allow_tags = True


class NodeListAdmin(admin.ModelAdmin):
    """ Provides a list of nodes for helping adding slivers to an slice"""
    
    list_display = [add_sliver_link, 'uuid', 'arch']
    actions = None
    list_filter = ['arch', 'set_state']
    search_fields = ['description', 'id', 'uuid']
    
    def changelist_view(self, request, slice_id, extra_context=None):
        self.slice_id = slice_id
        slice = Slice.objects.get(pk=slice_id)
        context = {'title': 'Select a node for slice "%s"' % slice.name,}
        context.update(extra_context or {})
        return super(NodeListAdmin, self).changelist_view(request, context)
    
    def queryset(self, request):
        """ Filter the node list to nodes where there are no slivers of this slice """
        qs = self.model._default_manager.get_query_set()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        qs = qs.exclude(pk__in=Node.objects.filter(sliver__slice=self.slice_id))
        return qs


class AddSliverAdmin(SliverAdmin):
    fields = ['description']
    
    def add_view(self, request, slice_id, node_id, form_url='', extra_context=None):
        self.slice_id = slice_id
        self.node_id = node_id
        slice = Slice.objects.get(pk=slice_id)
        node = Node.objects.get(pk=node_id)
        context = {'title': 'Add sliver in node "%s" (slice "%s")' % (node.description, slice.name),}
        context.update(extra_context or {})
        return super(AddSliverAdmin, self).add_view(request, form_url='', extra_context=context)
    
    def save_model(self, request, obj, *args, **kwargs):
        obj.node = Node.objects.get(pk=self.node_id)
        obj.slice = Slice.objects.get(pk=self.slice_id)
        super(AddSliverAdmin, self).save_model(request, obj, *args, **kwargs)
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        """ Determines the HttpResponse for the add_view stage. """
        opts = obj._meta
        pk_value = obj._get_pk_val()
        
        msg = 'The %(name)s "%(obj)s" was added successfully.' % {'name': force_text(opts.verbose_name), 'obj': force_text(obj)}
        # Here, we distinguish between different save types by checking for
        # the presence of keys in request.POST.
        if "_continue" in request.POST:
            # FIXME this doesn't work
            self.message_user(request, msg + ' ' + "You may edit it again below.")
            if "_popup" in request.POST:
                post_url_continue += "?_popup=1"
            return HttpResponseRedirect(post_url_continue % pk_value)
        
        if "_popup" in request.POST:
            return HttpResponse(
                '<!DOCTYPE html><html><head><title></title></head><body>'
                '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script></body></html>' % \
                (escape(pk_value), escapejs(obj)))
        elif "_addanother" in request.POST:
            self.message_user(request, msg + ' ' + ("You may add another %s below.") % force_text(opts.verbose_name))
            return HttpResponseRedirect('.')
        else:
            self.message_user(request, msg)
            if self.has_change_permission(request, None):
                post_url = reverse('admin:slices_slice_change', args=(self.slice_id,))
            else:
                post_url = reverse('admin:index',
                                   current_app=self.admin_site.name)
            return HttpResponseRedirect(post_url)


class SliverInline(admin.TabularInline):
    # TODO nested inlines: https://code.djangoproject.com/ticket/9025
    model = Sliver
    form = SliverInlineAdminForm
    max_num = 0
    readonly_fields = ['instance_sn']


class SlicePropInline(admin.TabularInline):
    model = SliceProp
    extra = 0


class SliceAdmin(ChangeViewActionsMixin):
    list_display = ['name', 'uuid', 'instance_sn', 'vlan_nr', colored('set_state', STATE_COLORS), 'num_slivers',
        admin_link('template'), 'expires_on', ]
    list_filter = ['set_state', 'template']
    readonly_fields = ['instance_sn', 'new_sliver_instance_sn', 'expires_on']
    date_hierarchy = 'expires_on'
    search_fields = ['name', 'uuid']
    inlines = [SlicePropInline,SliverInline]
    actions = [reset_selected, renew_selected_slices]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', ('template', 'exp_data'), 
                       'vlan_nr', 'set_state', 'users', 'instance_sn', 
                       'new_sliver_instance_sn', 'expires_on'),
        }),
        ('Public key', {
            'classes': ('collapse',),
            'fields': ('pubkey',)
        }),)
    change_form_template = "admin/slices/slice/change_form.html"
    change_view_actions = [('renew', renew_selected_slices, '', ''),
                           ('reset', reset_selected, '', '')]
    
    def get_urls(self):
        urls = super(SliceAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        extra_urls = patterns("", 
            url("^(?P<slice_id>\d+)/add_sliver/$", NodeListAdmin(Node, admin_site).changelist_view),
            url("^(?P<slice_id>\d+)/add_sliver/(?P<node_id>\d+)", AddSliverAdmin(Sliver, admin_site).add_view),)
        return extra_urls + urls


class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'type', 'arch', 'data', 'is_active']
    list_filter = ['is_active', 'type', 'arch']
    search_fields = ['name', 'description', 'type', 'arch']


admin.site.register(Sliver, SliverAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Template, TemplateAdmin)
