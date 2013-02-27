from django.contrib.gis.shortcuts import render_to_kml
from django.core.urlresolvers import reverse
from django.shortcuts import render

from gis.models import NodeGeolocation

#TODO generalization of those functions to allow using other models.
#       --> add new parameter == Model
#       --> do the querys using this model
def generate_kml(request):
    """
    Generate a Google Maps compatible KML file containing
    the nodes gelocation information.
    """
    locations = NodeGeolocation.objects.all().values('node__name', 'node__description', 'geolocation')

    for loc in locations:
        loc['lat'], loc['lng'] = loc['geolocation'].split(',')

    return render_to_kml('locations.kml', {'locations':locations})

def map(request):
    """
    Render a map using Google Maps API and loading markers from a KML.
    """
    iframe = request.GET.get("iframe", False)
    # map options and kml url
    kml = request.build_absolute_uri(reverse('gis_kml_nodes'))
    opts = {
        'iframe': iframe,
        'kml': kml,
        'center': {'lat': 44.813029, 'lng': 15.977895},
        'zoom': 5
    }
    return render(request, 'map.html', opts)
