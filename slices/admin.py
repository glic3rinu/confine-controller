from django.contrib import admin
from models import Slice, Sliver, MemoryRequest, StorageRequest, CPURequest, NetworkRequest
from utils.widgets import ShowText
from django import forms 

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


class SliverAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'slice', 'node', 'cpurequest', 'memoryrequest', 'storagerequest']
    list_filter = ['storagerequest__type', 'cpurequest__type', 'networkrequest__type']
    inlines = [CPURequestInline, MemoryRequestInline, StorageRequestInline, NetworkRequestInline]


class SliverForm(forms.ModelForm):
    node = forms.CharField(label="Node", widget=ShowText(bold=True))
    url = forms.CharField(label="Node URL", widget=ShowText(bold=True))
    
    class Meta:
        fields = ('node', 'url', 'status',)
    
    def __init__(self, *args, **kwargs):
        super(SliverForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.initial['node'] = instance.node
            self.initial['url'] = instance.node.url


class SliverInline(admin.TabularInline):
    model = Sliver
    form = SliverForm
    max_num = 0    

def users(self):
    return ",".join(self.user.all().values_list('username', flat=True))

class SliceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', users ]
    inlines = [SliverInline]

admin.site.register(Slice, SliceAdmin)
admin.site.register(Sliver, SliverAdmin)
