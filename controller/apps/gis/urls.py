"""
URLconf for gis.
"""

from django.conf.urls import patterns, url

from gis.views import generate_kml, map

urlpatterns = patterns('',
    url(r'^nodes.kml', generate_kml, name='gis_kml_nodes'),
    url(r'^map/$', map, name='gis_map'),
)

