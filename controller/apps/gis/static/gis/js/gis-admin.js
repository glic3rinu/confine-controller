
/*
Integration for Google Maps in the django admin.

How it works:

You have an address field on the page.
Enter an address and an on change event will update the map
with the address. A marker will be placed at the address.
If the user needs to move the marker, they can and the geolocation
field will be updated.

Only one marker will remain present on the map at a time.

This script expects:

<input type="text" name="address" id="id_address" />
<input type="text" name="geolocation" id="id_geolocation" />

<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>

*/

function googleMapAdmin() {

    var map;
    var marker;
    var markers;

    var self = {
        initialize: function() {
            var lat = 0;
            var lon = 0;
            var zoom = 2;
            // set up initial map to be world view. also, add change
            // event so changing address will update the map
            existinglocation = self.getExistingLocation();
            if (existinglocation) {
                lat = existinglocation.lat;
                lon = existinglocation.lon;
                zoom = 12;
            }

            map = new OpenLayers.Map('map_canvas', {
                controls: [
                    new OpenLayers.Control.PanZoom(),
                    new OpenLayers.Control.Permalink(),
                    new OpenLayers.Control.Navigation()
                ]
            });
            map.addLayer(new OpenLayers.Layer.OSM("OpenStreetMap"));

            var lonlat = new OpenLayers.LonLat(lon, lat).transform(
                    new OpenLayers.Projection("EPSG:4326"),
                    map.getProjectionObject()
                );
            map.setCenter(lonlat, zoom);

            // init markers layer
            markers = new OpenLayers.Layer.Markers("Markers");
            map.addLayer(markers);

            if (existinglocation) {
                self.setMarker(lonlat);
            }

            $("#id_address").change(function() {self.codeAddress();});
            $("#id_geolocation").change(function() {
                var location = self.getExistingLocation();
                if(location) {
                    lonlat = new OpenLayers.LonLat(location.lon, location.lat).transform(
                            new OpenLayers.Projection("EPSG:4326"),
                            map.getProjectionObject()
                        );
                    self.setMarker(lonlat);
                    map.setCenter(lonlat, 12);
                }
            });
        },

        getExistingLocation: function() {
            var geolocation = $("#id_geolocation").val();
            if (geolocation) {
                var latlon = geolocation.split(',');
                return { 
                    'lat': latlon[0],
                    'lon': latlon[1]
                }
            }
            return null;
        },

        codeAddress: function() {
            var address = $("#id_address").val();
            OpenLayers.Request.GET({
               url:  "http://nominatim.openstreetmap.org/search/" + address,
               params: {format: "json"},
               scope: self,
               failure: self.requestFailure,
               success: self.requestSuccess,
               headers: {"Content-Type": "application/x-www-form-urlencoded"}
            });
        },
        requestFailure: function(response) {
            alert("An error occurred while communicating with the OpenLS service. Please try again.");
        },

        requestSuccess: function(response) {
            var format = new OpenLayers.Format.JSON();
            var output = format.read(response.responseText);
            if (output[0]) {
                var geometry = {lat: output[0].lat, lon: output[0].lon};
                var foundPosition = new OpenLayers.LonLat(geometry.lon, geometry.lat).transform(
                            new OpenLayers.Projection("EPSG:4326"),
                            map.getProjectionObject()
                        );
                map.setCenter(foundPosition, 14);
                self.setMarker(foundPosition);
                self.updateGeolocation(geometry);
            } else {
                alert("Sorry, no address found");
            }
        },

        setMarker: function(location) {
            markers.clearMarkers();
   	    var size = new OpenLayers.Size(21,25);
            var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
            var icon = new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png',size,offset);
            markers.addMarker(new OpenLayers.Marker(location, icon.clone()));

            /* TODO!!! --> use Feature for making it draggable
            var draggable = Options.draggable || false;
            if (draggable) {
                self.addMarkerDrag(marker);
            }*/
        },

        addMarkerDrag: function(marker) {
            // TODO
        },

        updateGeolocation: function(location) {
            $("#id_geolocation").val(location.lat + "," + location.lon);
        }
    }

    return self;
}

$(document).ready(function() {
    var googlemap = googleMapAdmin();
    googlemap.initialize();
});