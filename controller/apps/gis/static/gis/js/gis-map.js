/** Clousure for map based on OpenLayers: OSM and KML layers **/
function OsmMap(lat, lng, zoom, kml_url) {

    // Popup for displaying marker info //
    function onPopupClose(evt) {
        selectControl.unselect(this.feature);
    }

    /** display the popup updating location and information **/
    function onFeatureSelect(evt) {
        feature = evt.feature;
        if(feature.attributes.name == null) {
            // Center the map and zoom in to the selected feature
            map.panTo(feature.geometry.getBounds().getCenterLonLat());
            map.zoomTo(map.zoom + 1);
            return; // Don't create the popup
        }
        popup = new OpenLayers.Popup.FramedCloud("featurePopup",
                                 feature.geometry.getBounds().getCenterLonLat(),
                                 new OpenLayers.Size(100,100),
                                 "<h2>" + feature.attributes.name + "</h2>" +
                                 feature.attributes.description,
                                 null, true, onPopupClose);
        feature.popup = popup;
        popup.feature = feature;
        map.addPopup(popup);
    }

    /** hide the popup **/
    function onFeatureUnselect(evt) {
        feature = evt.feature;
        if (feature.popup) {
            popup.feature = null;
            map.removePopup(feature.popup);
            feature.popup.destroy();
            feature.popup = null;
        }
    }

    // Define three colors that will be used to style the cluster features
    // depending on the number of features they contain.
    var colors = {
        low: "rgb(28, 28, 200)", /** neutral color, different than node states! **/
        middle: "rgb(20, 28, 200)",
        high: "rgb(28, 28, 200)"
    };

    // Define three rules to style the cluster features.
    var lowRule = new OpenLayers.Rule({
        filter: new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.LESS_THAN,
            property: "count",
            value: 10
        }),
        symbolizer: {
            fillColor: colors.low,
            fillOpacity: 0.9,
            strokeColor: colors.low,
            strokeOpacity: 0.5,
            strokeWidth: 12,
            pointRadius: 10,
            label: "${count}",
            labelOutlineWidth: 1,
            fontColor: "#ffffff",
            fontOpacity: 0.8,
            fontSize: "12px"
        }
    });
    var middleRule = new OpenLayers.Rule({
        filter: new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.BETWEEN,
            property: "count",
            lowerBoundary: 10,
            upperBoundary: 30
        }),
        symbolizer: {
            fillColor: colors.middle,
            fillOpacity: 0.9,
            strokeColor: colors.middle,
            strokeOpacity: 0.5,
            strokeWidth: 12,
            pointRadius: 15,
            label: "${count}",
            labelOutlineWidth: 1,
            fontColor: "#ffffff",
            fontOpacity: 0.8,
            fontSize: "12px"
        }
    });
    var highRule = new OpenLayers.Rule({
        filter: new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.GREATER_THAN,
            property: "count",
            value: 30
        }),
        symbolizer: {
            fillColor: colors.high,
            fillOpacity: 0.9, 
            strokeColor: colors.high,
            strokeOpacity: 0.5,
            strokeWidth: 12,
            pointRadius: 20,
            label: "${count}",
            labelOutlineWidth: 1,
            fontColor: "#ffffff",
            fontOpacity: 0.8,
            fontSize: "12px"
        }
    });

    // Create a Style that uses the three previous rules
    var style = new OpenLayers.Style(null, {
        rules: [lowRule, middleRule, highRule]
    });

    // KML Layer for displaying nodes //
    var kml_layer = new OpenLayers.Layer.Vector("KML", {
                protocol: new OpenLayers.Protocol.HTTP({
                    url: kml_url,
                    format: new OpenLayers.Format.KML({
                        extractStyles: true,
                        extractAttributes: true,
                        maxDepth: 2
                    })
                }),
                renderers: ['Canvas','SVG'],
                strategies: [
                    new OpenLayers.Strategy.Fixed(),
                    new OpenLayers.Strategy.AnimatedCluster({
                        distance: 45,
                        animationMethod: OpenLayers.Easing.Expo.easeOut,
                        animationDuration: 10,
                        threshold: 2
                    })
                ],
                styleMap:  new OpenLayers.StyleMap(style)
            });

    // Map init //
    var map = new OpenLayers.Map({
        div: "map_canvas",
        layers: [
            new OpenLayers.Layer.OSM({
                numZoomLevels: null,
                minZoomLevel: 8,
                maxZoomLevel: 15
            }),
            kml_layer
        ]});

    map.setCenter(
        new OpenLayers.LonLat(lng, lat ).transform(
            new OpenLayers.Projection("EPSG:4326"),
            map.getProjectionObject()
        ), zoom
    );

    // enable events the KML layer
    kml_layer.events.on({
        'featureselected': onFeatureSelect,
        'featureunselected': onFeatureUnselect
    });

    // init the select feature control and add to the map
    selectControl = new OpenLayers.Control.SelectFeature(kml_layer);
    map.addControl(selectControl);
    selectControl.activate();
    
    return map;
}
