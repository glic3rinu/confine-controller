from django.contrib.gis.shortcuts import render_to_kml
from django.core.urlresolvers import reverse
from django.shortcuts import render

from nodes.models import Node
from state.models import State

from .settings import GIS_MAP_CENTER, GIS_MAP_ZOOM

STATES_LEGEND = ['online', 'offline', 'unknown'] # aggregated states as in report
STATES_LIST = sorted([state[0] for state in State.NODE_STATES])

#TODO generalization of those functions to allow using other models.
#       --> add new parameter == Model
#       --> do the querys using this model
def generate_kml(request):
    """
    Generate a Google Maps compatible KML file containing
    the nodes gelocation information.
    """
    nodes = Node.objects.filter(gis__isnull=False).exclude(gis__geolocation='')
    return render_to_kml('locations.kml', {
        'locations': nodes,
        'states': STATES_LIST
    })

def map(request):
    """
    Render a map using Google Maps API and loading markers from a KML.
    NOTE: the KML URL must be publicly accessible as documented at Google API
    https://developers.google.com/maps/documentation/javascript/layers#KMLLayers
    """
    iframe = request.GET.get("iframe", False)
    # map options and kml url
    kml_url = request.build_absolute_uri(reverse('gis_kml_nodes'))
    opts = {
        'iframe': iframe,
        'kml_url': kml_url,
        'center': GIS_MAP_CENTER,
        'zoom': GIS_MAP_ZOOM,
        'states': STATES_LEGEND
    }
    return render(request, 'map.html', opts)
