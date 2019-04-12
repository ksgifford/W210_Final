var map;

function onEachFeature(feature, layer) {
  if (feature.properties) {
    label = feature.properties.label
    confidence = feature.properties.probability*100
    layer.bindPopup('Species: ' + label + '<br>' +
                    'Confidence: ' + confidence.toString().substr(0,4) +'%');}}

function initializePage(){
  var geojsonMarkerOptions = {
    radius: 8,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
  };

  map = L.map("map").setView([47.389655, -120.272218], 7);
  L.tileLayer(
    "https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw",
    {
      maxZoom: 18,
      attribution:
        'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
          '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
          'Imagery © <a href="http://mapbox.com">Mapbox</a>',
      id: "mapbox.light"
    }
  ).addTo(map);

  L.geoJSON(mapData, {
      pointToLayer: function (feature, latlng) {return L.circleMarker(latlng, geojsonMarkerOptions);
    },
    onEachFeature: onEachFeature
  }).addTo(map);
};
initializePage();
