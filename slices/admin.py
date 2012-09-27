from common.widgets import ShowText
from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from models import Sliver, SliverProp, IsolatedIface, PublicIface, PrivateIface, Slice, SliceProp, Template


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


class SliverAdmin(admin.ModelAdmin):
    list_display = ['description', 'id', 'instance_sn', 'node', 'slice']
    list_filter = ['slice__name',]
    search_fields = ['description', 'node__description', 'slice__name']
    inlines = [SliverPropInline, IsolatedIfaceInline, PublicIfaceInline, PrivateIfaceInline]


class SliverInlineForm(forms.ModelForm):
    """ 
    Read-only form for displaying slivers in slice admin change form.
    Also it provides popup links to each sliver admin change form.
    """
    #FIXME: js needed: when save popup the main form is not updated with the new/changed slivers
    #TODO: possible reimplementation when nested inlines support becomes available 
    sliver = forms.CharField(label="Sliver", widget=ShowText(bold=True))
    node = forms.CharField(label="Node", widget=ShowText(bold=True))
    url = forms.CharField(label="Node CN URL", widget=ShowText(bold=True))

    class Meta:
        # reset model field order
        fields = []
    
    def __init__(self, *args, **kwargs):
        super(SliverInlineForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            sliver_change = reverse('admin:slices_sliver_change', args=(instance.pk,))
            self.initial['sliver'] = mark_safe("""<a href='%s' id='add_id_user' 
                onclick='return showAddAnotherPopup(this);'>%s </a>""" % (sliver_change, instance))
            node_change = reverse('admin:nodes_node_change', args=(instance.node.pk,))
            self.initial['node'] = mark_safe("<a href='%s'>%s</a>" % (node_change, instance.node))
            self.initial['url'] = mark_safe("<a href='%s'>%s</a>" % (instance.node.cn_url, 
                instance.node.cn_url))


class SliverInline(admin.TabularInline):
    model = Sliver
    form = SliverInlineForm
    max_num = 0


class SlicePropInline(admin.TabularInline):
    model = SliceProp
    extra = 0


class SliceAdmin(admin.ModelAdmin):
    list_display = ['name', 'uuid', 'instance_sn', 'vlan_nr', 'set_state',
        'template', 'expires_on']
    list_filter = ['set_state']
    date_hierarchy = 'expires_on'
    search_fields = ['name', 'uuid']
    inlines = [SlicePropInline,SliverInline]


class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'type', 'arch', 'data', 'is_active']
    list_filter = ['is_active', 'type', 'arch']
    search_fields = ['name', 'description', 'type', 'arch']

admin.site.register(Sliver, SliverAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Template, TemplateAdmin)
