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
    places = []
    for loc in locations:
        try:
            loc['lat'], loc['lng'] = loc['geolocation'].split(',')
        except: # ignore not well
            continue
        places.append(loc)

    return render_to_kml('locations.kml', {'locations':places})

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
        'center': {'lat': 44.813029, 'lng': 15.977895},
        'zoom': 5
    }
    return render(request, 'map.html', opts)
