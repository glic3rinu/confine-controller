from django.contrib import admin
from models import Slice, Sliver, MemoryRequest, StorageRequest, CPURequest, NetworkRequest
from utils.widgets import ShowText
from django import forms 
import settings 
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


class MemoryRequestInline(admin.TabularInline):
    model = MemoryRequest
    max_num = 0
    
class StorageRequestInline(admin.TabularInline):
    model = StorageRequest
    max_num = 0
    
class CPURequestInline(admin.TabularInline):
    model = CPURequest
    max_num = 0

class NetworkRequestInline(admin.TabularInline):
    model = NetworkRequest
    extra = 0


class SliverAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'slice', 'node', 'cpurequest', 'memoryrequest', 'storagerequest']
    list_filter = ['storagerequest__type', 'cpurequest__type', 'networkrequest__type']
    inlines = [CPURequestInline, MemoryRequestInline, StorageRequestInline, NetworkRequestInline]

class SliverForm(forms.ModelForm):
    sliver = forms.CharField(label="Sliver", widget=ShowText(bold=True))
    node = forms.CharField(label="Node", widget=ShowText(bold=True))
    url = forms.CharField(label="Node URL", widget=ShowText(bold=True))
    
    class Meta:
        fields = ('sliver', 'node', 'url', 'status',)

    def __init__(self, *args, **kwargs):
        super(SliverForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            sliver_change = reverse('admin:slices_sliver_change', args=(instance.pk,))
            self.initial['sliver'] = mark_safe("<a href='%s'>%s</a>" % (sliver_change, instance))
            node_change = reverse('admin:nodes_node_change', args=(instance.node.pk,))
            self.initial['node'] = mark_safe("<a href='%s'>%s</a>" % (node_change, instance.node))
            self.initial['url'] = mark_safe("<a href='%s'>%s</a>" % (instance.node.url, instance.node.url))


class SliverInline(admin.TabularInline):
    model = Sliver
    form = SliverForm
    max_num = 0    

def users(slice):
    return slice.user.username
    # for now only one user x slice: replace with the following when we allow more
    #return ",".join(self.user.all().values_list('username', flat=True))


SLICE_STATE_COLORS = { settings.ONLINE: "green",
                       settings.OFFLINE: "red",}

def colored_status(slice):
    status = escape(slice.status)
    color = SLICE_STATE_COLORS.get(slice.status, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color, status)
colored_status.short_description = "status" 
colored_status.allow_tags = True
colored_status.admin_order_field = 'status'


class SliceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', users, colored_status ]
    list_filter = ['status']
    inlines = [SliverInline]

admin.site.register(Slice, SliceAdmin)
admin.site.register(Sliver, SliverAdmin)
