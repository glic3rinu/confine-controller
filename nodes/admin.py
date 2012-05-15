from django.contrib import admin
from models import Node, Storage, Memory, CPU, Interface, DeleteRequest
from django import forms
import settings
from django.utils.html import escape
from confine_utils.admin import admin_link_factory

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


class NodeAdmin(admin.ModelAdmin):
    list_display = ['hostname', admin_link_factory('url', description='URL'), 'architecture', colored_state ]
    list_filter = ['architecture', 'state']
    inlines = [CPUInline, MemoryInline, StorageInline, InterfaceInline]
    fieldsets = (
        (None, {
            'fields': (('owner'), ('hostname',), ('ip',), ('state',), ('architecture',), ('public_key',), ('uci',))
        }),
        ('Community node', {
            'fields': (('url',), ('latitude',), ('longitude',))
        }),
    )


class DeleteRequestAdmin(admin.ModelAdmin):
    model = DeleteRequest

admin.site.register(Node, NodeAdmin)
admin.site.register(DeleteRequest, DeleteRequestAdmin)
