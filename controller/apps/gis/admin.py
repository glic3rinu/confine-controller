from django.contrib import admin
from django.forms.widgets import TextInput
from django_google_maps import fields as map_fields

from controller.admin.utils import insertattr
from nodes.models import Node

from . import widgets as map_widgets
from .models import Geolocation, NodeGeolocation


class GisInline(admin.TabularInline):
    """ Base class for create an inline that provides geolocation info. """
    fields = ['address', 'geolocation']
    model = Geolocation
    max_num = 1
    formfield_overrides = {
        map_fields.AddressField: {
            'widget': map_widgets.OSMAddressWidget(attrs={'id': 'id_address', 'size':'80'})},
        map_fields.GeoLocationField: {
            'widget': TextInput(attrs={'id': 'id_geolocation'})},
    }
    verbose_name_plural = 'Geolocation'
    can_delete = False


class NodeGisInline(GisInline):
    """ Inline instantiation for node geolocation. """
    model = NodeGeolocation


# Monkey-Patching Section
insertattr(Node, 'inlines', NodeGisInline)
