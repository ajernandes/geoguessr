let panorama;
let map;
let map2;
let markers = [];

function initialize() {
  let position = prompt('Please the position bytes');
  position = hex2a(position)
  console.log(position)
  lat = parseFloat(position.split(",")[0]);
  lng = parseFloat(position.split(",")[1]);
  const location = { lat: lat, lng: lng };
  const locationStr = JSON.stringify({ lat: lat, lng: lng });
  document.getElementsByTagName("body")[0].setAttribute("pos", locationStr);


  panorama = new google.maps.StreetViewPanorama(
    document.getElementById("pano"),
    {
      position: location,
      addressControl: false,
      fullscreenControl: false,
      linksControl: false,
      groundOverlay: false,
      motionTracking: false,
      motionTrackingControl: false,
      showRoadLabels: false,
    }
  );
    map = new google.maps.Map(
      document.getElementById("map"), 
      {
        zoom: 1,
        center: { lat: 0, lng: 0 },
        streetViewControl: false,
    });
    map2 = new google.maps.Map(
      document.getElementById("results"), 
      {
        zoom: 4,
        center: { lat: 0, lng: 0 },
        streetViewControl: false,
    });
    map.addListener("click", (location) => {
      for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
      }
      markers = [];
        const marker = new google.maps.Marker({
        position: location.latLng.toJSON(),
        map: map,
      });
      markers.push(marker); 
    });
    panorama.addListener("pov_changed", () => {
      document.getElementById("arrow").setAttribute("style", "transform: rotate(" + panorama.getPov().heading.toString() + "deg);");
    });
}


  function hex2a(hexx) {
    var hex = hexx.toString();//force conversion
    var str = '';
    for (var i = 0; (i < hex.length && hex.substr(i, 2) !== '00'); i += 2)
        str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
    return str;
}

function submit() {
  let cords = markers[0].getPosition().toJSON();
  var iconBase = 'https://maps.google.com/mapfiles/kml/shapes/';
  let pos = document.getElementsByTagName("body")[0].getAttribute("pos");
  pos = JSON.parse(pos);

  getScore(getDistanceFromLatLonInKm(cords.lat, cords.lng, pos.lat, pos.lng), cords, pos)
}

async function getData(url) {
  let response = await fetch(url);
  let data = await response.json();
  return data;
}

function getScore(distance, cords, pos) {
  let distancem = distance / 10;
  
  let score = -500*(Math.log(distancem / 100_000)) - 250;

  if (score < 1) score = 0;
  if (score > 5000) score = 5000;
  score = Math.round(score);
  distance = Math.round(distance);

  document.getElementById("map").setAttribute("style", "display:none");
  document.getElementById("pano").setAttribute("style", "display:none");
  document.getElementById("table").setAttribute("style", "display:none");
  document.getElementById("results").setAttribute("style", "");
  //document.getElementById("resultstxt").setAttribute("style", "");
  //document.getElementById("dist").innerHTML = distance + " Km";
  //document.getElementById("pts").innerHTML = score + " points";
  const svgMarker = {
    path:
      "M10.453 14.016l6.563-6.609-1.406-1.406-5.156 5.203-2.063-2.109-1.406 1.406zM12 2.016q2.906 0 4.945 2.039t2.039 4.945q0 1.453-0.727 3.328t-1.758 3.516-2.039 3.070-1.711 2.273l-0.75 0.797q-0.281-0.328-0.75-0.867t-1.688-2.156-2.133-3.141-1.664-3.445-0.75-3.375q0-2.906 2.039-4.945t4.945-2.039z",
    fillColor: "blue",
    fillOpacity: 1,
    strokeWeight: 0,
    rotation: 0,
    scale: 2,
    anchor: new google.maps.Point(15, 30),
  };

  const locations = [ pos, cords ];

  map2.setCenter(pos)

  const line = new google.maps.Polyline({
    path:locations,
    geodesic: true,
    strokeColor: "#aaaaaa",
    strokeWeight: 5,
  })
  line.setMap(map2);

  const marker1 = new google.maps.Marker({
    position: cords,
    map: map2,
  });

  const marker2 = new google.maps.Marker({
    position: pos,
    map: map2,
    icon: svgMarker,
  });

  alert(score + " Points\n" + distance + "Km");
}

function smallerMap() {
  document.getElementById("map").setAttribute("style", "display:none; position: absolute; bottom: 0; right: 0; z-index: 10;");
}

function biggerMap() {
  document.getElementById("map").setAttribute("style", "height: 80%; width: 80%; position: absolute; bottom: 0; right: 0; z-index: 10;");
}

function toStart() {
  let pos = document.getElementsByTagName("body")[0].getAttribute("pos");
  pos = JSON.parse(pos);
  panorama.setPosition(pos);
}

function getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) {
  var R = 6371; // Radius of the earth in km
  var dLat = deg2rad(lat2-lat1);  // deg2rad below
  var dLon = deg2rad(lon2-lon1); 
  var a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
    Math.sin(dLon/2) * Math.sin(dLon/2)
    ; 
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  var d = R * c; // Distance in km
  return d;
}

function deg2rad(deg) {
  return deg * (Math.PI/180)
}