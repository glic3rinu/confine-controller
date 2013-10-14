from django.conf import settings

GIS_MAP_CENTER = getattr(settings, 'GIS_MAP_CENTER', {'lat': 44.813029, 'lng': 15.977895})
GIS_MAP_ZOOM = getattr(settings, 'GIS_MAP_ZOOM', 5)
