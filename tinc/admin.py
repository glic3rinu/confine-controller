from django.contrib import admin
from models import TincAddress, Island, Gateway


class TincAddressAdmin(admin.ModelAdmin):
    list_display = ['ip_addr', 'port', 'island', 'server']
    list_filter = ['island__name', 'port']
    search_fields = ['ip_addr', 'island__name', 'island__description', 'server__tinc_name'] 


class IslandAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'description']
    search_fields = ['name', 'description']


class GatewayAdmin(admin.ModelAdmin):
    list_display = ['tinc_name', 'id' ]

admin.site.register(TincAddress, TincAddressAdmin)
admin.site.register(Island, IslandAdmin)
admin.site.register(Gateway, GatewayAdmin)
