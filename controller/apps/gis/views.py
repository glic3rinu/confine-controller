from django.contrib.gis.shortcuts import render_to_kml

from nodes.models import Node

def generate_kml(request):
    """ Generate a kml file to show nodes location into a map """
    locations = Node.objects.all().values('name','description','geolocation')

    for loc in locations:
        loc['lat'], loc['lng'] = loc['geolocation'].split(',')

    return render_to_kml('locations.kml', {'locations':locations})
