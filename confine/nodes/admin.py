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

def colored_state(node):
    state = escape(node.state)
    color = NODE_STATE_COLORS.get(node.state, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color, state)
colored_state.short_description = "State" 
colored_state.allow_tags = True
colored_state.admin_order_field = 'state'


def url_link(self):
    return '<a href="%s">%s' % (self.url, self.url)
url_link.short_description = "URL"
url_link.allow_tags = True
url_link.admin_order_field = 'url'

class NodeAdmin(admin.ModelAdmin):
    list_display = ['hostname', url_link, 'architecture', colored_state ]
    list_filter = ['architecture', 'state']
    inlines = [CPUInline, MemoryInline, StorageInline, InterfaceInline]
    fieldsets = (
        (None, {
            'fields': (('hostname',), ('state',), ('architecture',), ('public_key',), ('uci',))
        }),
        ('Community node', {
            'fields': (('url',), ('latitude',), ('longitude',))
        }),
    )



admin.site.register(Node, NodeAdmin)
