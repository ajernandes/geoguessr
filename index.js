let map;
let markers = [];

function initialize() {
  let position = prompt('Please the position bytes');
  position = hex2a(position)
  console.log(position)
  document.getElementsByTagName("body")[0].setAttribute("pos", position);
  lat = parseFloat(position.split(",")[0]);
  lng = parseFloat(position.split(",")[1]);
  const location = { lat: lat, lng: lng };

  const panorama = new google.maps.StreetViewPanorama(
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
  cords = cords.lat + "," + cords.lng;
  console.log(cords);
  let pos = document.getElementsByTagName("body")[0].getAttribute("pos");
  
  const proxyurl = "https://cors-anywhere.herokuapp.com/";
  getData(proxyurl + "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=" + cords + "&destinations=" + pos + "&key=AIzaSyA9PAn87ZMK3SB5SNJlC9ATOAediOgg6IU").then(data => getScore(data.rows[0].elements[0].distance.value))
}

async function getData(url) {
  let response = await fetch(url);
  let data = await response.json();
  return data;
}

function getScore(distance) {
  console.log(distance)
  let score = Math.round(-1*Math.exp(-distance/5000)-(1/5000000000)*distance*distance + 5000.5)
  alert(score);
}

function smallerMap() {
  document.getElementById("map").setAttribute("style", "display:none; position: absolute; bottom: 0; right: 0; z-index: 10;");
}

function biggerMap() {
  document.getElementById("map").setAttribute("style", "height: 80%; width: 80%; position: absolute; bottom: 0; right: 0; z-index: 10;");
}