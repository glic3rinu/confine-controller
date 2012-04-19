from django.contrib import admin
from models import Node, Storage, Memory, CPU, Interface
from django import forms
import settings
from django.utils.html import escape

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
    
class InterfaceInline(admin.TabularInline):
    model = Interface
    extra = 1
    

NODE_STATE_COLORS = { settings.ONLINE: "green",
                      settings.PROJECTED: "darkorange",
                      settings.DISABLED: "gray",
                      settings.OFFLINE: "red",}

def colored_status(node):
    status = escape(node.status)
    color = NODE_STATE_COLORS.get(node.status, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color, status)
colored_status.short_description = "status" 
colored_status.allow_tags = True
colored_status.admin_order_field = 'status'


def url_link(self):
    return '<a href="%s">%s' % (self.url, self.url)
url_link.short_description = "URL"
url_link.allow_tags = True
url_link.admin_order_field = 'url'

class NodeAdmin(admin.ModelAdmin):
    list_display = ['hostname', url_link, 'architecture', colored_status ]
    list_filter = ['architecture', 'status']
    inlines = [CPUInline, MemoryInline, StorageInline, InterfaceInline]
    fieldsets = (
        (None, {
            'fields': (('hostname',), ('status',), ('architecture',), ('public_key',), ('uci',))
        }),
        ('Community node', {
            'fields': (('url',), ('latitude',), ('longitude',))
        }),
    )



admin.site.register(Node, NodeAdmin)
