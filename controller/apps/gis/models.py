from django_google_maps import fields as map_fields

from django.db import models

from nodes.models import Node


class Geolocation(models.Model):
    """
    Base class for introduce geolocation info into a model.
    If you want to extend an existing model for having geolocation
    information you only need to create a new child class with
    a field that relationate it with those model.
    
    E.g. For a model with name Foo:
        # Create child class, defining a field to associate with
        # the related model.
        class FooGeolocation(Geolocation):
            foo = models.ForeignKey(Foo, *options)
        
        # Inject into admin iface using Monkey-Patching (admin.py file)
        insert_inline(Foo, GisInline)
    """
    class Meta:
        abstract = True

    address = map_fields.AddressField(max_length=200, blank=True, null=True,
        help_text='Enter the node location name (street, city, region...) '
                  'The marker will be updated automatically.')
    geolocation = map_fields.GeoLocationField(max_length=100, blank=True, null=True,
        help_text='Geographic latitude and longitude. Updated automatically '
                  'using the address. You can drag the marker in the map to '
                  'make any correction if needed.')

    @property
    def lat(self):
        return self.geolocation.lat

    @property
    def lon(self):
        return self.geolocation.lon

class NodeGeolocation(Geolocation):
    """ Class for append geolocation information to a Node """
    node = models.OneToOneField(Node, primary_key=True, related_name='gis')
