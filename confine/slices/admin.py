from django.contrib import admin
from models import Slice, Sliver, MemoryRequest, StorageRequest, CPURequest, NetworkRequest
from utils.widgets import ShowText
from django import forms 
import settings 
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


STATE_COLORS = { settings.ALLOCATED: "darkorange",
                 settings.DEPLOYED: "magenta",
                 settings.STARTED: "green" 
               }

def colored_state(self):
    state = escape(self.state)
    color = STATE_COLORS.get(self.state, "black")
    return "<b><span style='color: %s;'>%s</span></b>" % (color, state)
colored_state.short_description = "State" 
colored_state.allow_tags = True
colored_state.admin_order_field = 'state'


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
    list_display = ['__unicode__', 'slice', 'node', 'cpurequest', 'memoryrequest', 'storagerequest', colored_state]
    list_filter = ['storagerequest__type', 'cpurequest__type', 'networkrequest__type', 'state']
    inlines = [CPURequestInline, MemoryRequestInline, StorageRequestInline, NetworkRequestInline]

class SliverForm(forms.ModelForm):
    """ 
        Read-only form for displaying slivers in slice change form.
        Also it provides popup links to each sliver change form.
    """

    sliver = forms.CharField(label="Sliver", widget=ShowText(bold=True))
    node = forms.CharField(label="Node", widget=ShowText(bold=True))
    url = forms.CharField(label="Node URL", widget=ShowText(bold=True))
    state = forms.CharField(label="State", widget=ShowText(bold=True))
    
    class Meta:
        # reset model field order
        fields = []
    
    def __init__(self, *args, **kwargs):
        super(SliverForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            sliver_change = reverse('admin:slices_sliver_change', args=(instance.pk,))
            #FIXME: popup does not close on save submit
            self.initial['sliver'] = mark_safe("<a href='%s' onclick='return showAddAnotherPopup(this);'>%s </a>" % (sliver_change, instance))
            node_change = reverse('admin:nodes_node_change', args=(instance.node.pk,))
            self.initial['node'] = mark_safe("<a href='%s'>%s</a>" % (node_change, instance.node))
            self.initial['url'] = mark_safe("<a href='%s'>%s</a>" % (instance.node.url, instance.node.url))
            self.initial['state'] = mark_safe(colored_state(instance))

    

class SliverInline(admin.TabularInline):
    model = Sliver
    form = SliverForm
    max_num = 0    

def users(slice):
    return slice.user.username
    # for now only one user x slice: replace with the following when we allow more:
    #return ",".join(self.user.all().values_list('username', flat=True))

class SliceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', users, colored_state ]
    list_filter = ['state']
    inlines = [SliverInline]


admin.site.register(Slice, SliceAdmin)
admin.site.register(Sliver, SliverAdmin)
