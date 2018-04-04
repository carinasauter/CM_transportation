function addFrame(latitude, longitude) {
	var lat_degrees = latitude.substring(0,2);
	var lat_minutes = latitude.substring(2,4) + "." + latitude.substring(5,);
	var googleLat = lat_degrees + " " + lat_minutes;
	var lon_degrees = longitude.substring(0,3);
	var lon_minutes = longitude.substring(3,5) + "." + longitude.substring(6,);
	var googleLon = "-" + lon_degrees + " " + lon_minutes;
	var destination = googleLat + "," + googleLon;
 	var stringToAppend = '<div id="iframecontent"><iframe width="600" height="450" frameborder="0" style="border:0" src="https://www.google.com/maps/embed/v1/place?key=AIzaSyCBaUAaH88OX-p0kLtdp8Ap2bPs4X2RpTU&q=' + destination + '" allowfullscreen></iframe></div>';
	$('#iframecontainer').append(stringToAppend);
};

function appendRequest(data) {
	var stringToAppend = 'Alex has been asked to come home. Waiting for response...';
	$('#request').append(stringToAppend);
	$('#response').empty();
}

$(document).ready(
	function() {
		$('#comeHomeButton').on('click', function() {
			$.getJSON('/triggerComeHome',
				function(data) {
					$('#request').empty();
					appendRequest(data);
        	});
    	return false;
    });
});

$(document).ready(
	function() {
		$('#getLocationButton').on('click', function() {
			$.getJSON('/getLocation',
				function(data) {
					$('#iframecontainer').empty();
					var location = data['location'];
					var latitude = location['lat'];
					var longitude = location['lon'];
					addFrame(latitude, longitude);
        	});
    	return false;
    });
});

var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('my_response', function (data) {
  $('#response').append("Alex is coming home!");
});