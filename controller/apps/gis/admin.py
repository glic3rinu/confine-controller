from gis import widgets as map_widgets
from django_google_maps import fields as map_fields

from django.forms.widgets import TextInput

from controller.admin.utils import insert_inline
from gis.models import Geolocation, NodeGeolocation
from nodes.models import Node
#from permissions.admin import PermissionGenericTabularInline
from django.contrib import admin

class GisInline(admin.TabularInline):
    """ Base class for create an inline that provides geolocation info. """
    class Meta:
        abstract = True

    model = Geolocation
    max_num = 1
    fields = ['address', 'geolocation']
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.OSMAddressWidget(attrs={'id': 'id_address', 'size':'80'})},
        map_fields.GeoLocationField: {'widget': TextInput(attrs={'id': 'id_geolocation'})},
    }
    verbose_name_plural = 'Geolocation'
    can_delete = False

class NodeGisInline(GisInline):
    """ Inline instantiation for node geolocation. """
    model = NodeGeolocation

# Monkey-Patching Section
insert_inline(Node, NodeGisInline)
