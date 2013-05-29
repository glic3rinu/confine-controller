
/*
Integration for Open Street Maps in the django admin.

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

<script type="text/javascript" src="OpenLayers.js"></script>

*/

function openLayersAdmin() {

    var map;
    var vectors;

    epsg4326 = new OpenLayers.Projection("EPSG:4326");
    epsg900913 = new OpenLayers.Projection("EPSG:900913");

    var self = {
        initialize: function() {
            var lat = 0, lon = 0, zoom = 2;
            
            // set up initial map to be world view. also, add change
            var existinglocation = self.getExistingLocation();
            if (existinglocation) {
                lat = existinglocation.lat;
                lon = existinglocation.lon;
                zoom = 12;
            }
            
            map = new OpenLayers.Map("map_canvas");

            var osm = new OpenLayers.Layer.OSM("OpenStreetMap");
            vectors = new OpenLayers.Layer.Vector("Vector Layer");
            map.addLayers([osm, vectors]);

            var center = new OpenLayers.LonLat(lon, lat).transform(epsg4326, epsg900913);
            self.setMarker(center);
            self.addMarkerDrag();
            
            map.setCenter(center, zoom);

            if (existinglocation) {
                self.setMarker(center);
            }

            // add listeners to manage form fields changes
            $("#id_address").change(function() {self.codeAddress();});
            $("#id_geolocation").change(function() {
                var location = self.getExistingLocation();
                if(location) {
                    lonlat = new OpenLayers.LonLat(location.lon, location.lat)
                        .transform(epsg4326, epsg900913);
                    self.setMarker(lonlat);
                    map.setCenter(lonlat, 12);
                }
            });
        },

        getExistingLocation: function() {
            /** checks (and returns if any) initial geolocation data **/
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
            /** geocoding based on address form field value  **/
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
                var foundPosition = new OpenLayers.LonLat(geometry.lon, geometry.lat)
                        .transform(epsg4326, epsg900913);
                map.setCenter(foundPosition, 14);
                self.setMarker(foundPosition);
                self.updateGeolocation(geometry);
            } else {
                alert("Sorry, no address found");
            }
        },

        setMarker: function(center) {
            /**
             * update the marker position (clear + create strategy)
             * @param center: coords in map projection (epsg900913)
             **/
            vectors.removeAllFeatures();
            var point = new OpenLayers.Geometry.Point(center.lon, center.lat);
            vectors.addFeatures([
                new OpenLayers.Feature.Vector(point/*, {vcid:'3243223'}, {
                    externalGraphic: 'http://www.openlayers.org/dev/img/marker.png',
                        graphicWidth: 21, graphicHeight: 25
                    }*/)
            ]);
        },

        addMarkerDrag: function() {
            /** add drag feature for vectors layer **/
            drag = new OpenLayers.Control.DragFeature(vectors, {
                autoActivate: true,
                onComplete: function() {
                    // clone the geometry for not change the marker!
                    var coord = this.feature.geometry.clone();
                    coord.transform(epsg900913, epsg4326);
                    self.updateGeolocation(new OpenLayers.LonLat(coord.x, coord.y));
                }
            });
            map.addControl(drag);
        },

        updateGeolocation: function(location) {
            /** update geolocation form field with new location coordinates **/
            $("#id_geolocation").val(location.lat + "," + location.lon);
        }
    }

    return self;
}

$(document).ready(function() {
    var openmap = openLayersAdmin();
    openmap.initialize();
});
