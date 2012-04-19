from django.contrib import admin
from models import Node, Storage, Memory, CPU, CommunityLink, GatewayLink, LocalLink, DirectLink
from django import forms
import settings

class StorageInlineForm(forms.ModelForm):
    types = forms.MultipleChoiceField(choices=settings.STORAGE_CHOICES)

class StorageInline(admin.TabularInline):
    model = Storage
    max_num = 0
    form = StorageInlineForm

class MemoryInline(admin.TabularInline):
    model = Memory
    max_num = 0

class CPUInline(admin.TabularInline):
    model = CPU
    max_num = 0
    
class CommunityLinkInline(admin.TabularInline):
    model = CommunityLink
    extra = 0
    
class GatewayLinkInline(admin.TabularInline):
    model = GatewayLink
    extra = 0
    
class LocalLinkInline(admin.TabularInline):
    model = LocalLink
    extra = 0
    
class DirectLinkInline(admin.TabularInline):
    model = DirectLink
    extra = 0
    

def url_link(self):
    return '<a href="%s">%s' % (self.url, self.url)
url_link.short_description = "URL"
url_link.allow_tags = True

class NodeAdmin(admin.ModelAdmin):
    list_display = ['hostname', url_link, 'architecture', 'status' ]
    list_filter = ['architecture', 'status']
    inlines = [CPUInline, MemoryInline, StorageInline, CommunityLinkInline, GatewayLinkInline, LocalLinkInline, DirectLinkInline]


admin.site.register(Node, NodeAdmin)
