"""
URLconf for gis.
"""

from django.conf.urls import patterns, include, url

from controller.apps.nodes.views import generate_kml

urlpatterns = patterns('',
    # KML Nodes Map
    url(r'^get_nodes_kml/$', generate_kml, name='gis_kml_nodes'),)


