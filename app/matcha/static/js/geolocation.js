function getLocation() {
    let xmlhttp;
    let long;
    let lat;

    navigator.geolocation.getCurrentPosition(function (position) {
            $('#alert_box').addClass('hide');
            long = position.coords.longitude;
            lat = position.coords.latitude;
            let xmlhttp = new XMLHttpRequest();
            xmlhttp.open("POST", "_treatlocation", true);
            xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xmlhttp.send("longitude=" + long + "&latitude=" + lat);
            let url = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + lat + "," + long + '&sensor=true' +
                '&key=AIzaSyA5YEbiuG6XmMYh9dhNBHsP4i4I3W4paR8';
            let xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function () {
                if (this.readyState === 4 && this.status === 200) {
                    $('#alert_box').fadeIn();
                    $('#alert_box').removeClass('hide');
                    $('#alert_message').html("Your location was updated");
                }
            };
            xhr.open('POST', url, true);
            xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhr.send();
        },
        function () {
            $.getJSON('http://ip-api.com/json', function (data) {
                long = data["lon"];
                lat = data["lat"];
                xmlhttp = new XMLHttpRequest();
                xmlhttp.onreadystatechange = function () {
                    if (this.readyState === 4 && this.status === 200) {
                        $('#alert_box').fadeIn();
                        $('#alert_box').removeClass('hide');
                        $('#alert_message').html("Your location was updated");
                    }
                };
                xmlhttp.open("POST", "_treatlocation", true);
                xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xmlhttp.send("longitude=" + long + "&latitude=" + lat);
            });
        });
    $('#alert_box').fadeIn();
    $('#alert_box').removeClass('hide');
    $('#alert_message').html("Please wait...");
}

function showPosition(position) {
    let long = Number(document.getElementById("longitude").innerText);
    let lat = Number(document.getElementById("latitude").innerText);

    let latlon = lat + "," + long;
    let img_url = "https://maps.googleapis.com/maps/api/staticmap?center="
        + latlon + "&zoom=14&size=400x300&key=AIzaSyA5YEbiuG6XmMYh9dhNBHsP4i4I3W4paR8";
    document.getElementById("map").innerHTML = "<img src='" + img_url + "'>";
}

function myMap() {
    let long = Number(document.getElementById("longitude").innerText);
    let lat = Number(document.getElementById("latitude").innerText);

    let myLatLng = {lat: lat, lng: long};
    // Create a map object and specify the DOM element
    // for display.
    let map = new google.maps.Map(document.getElementById('map'), {
        center: myLatLng,
        zoom: 15
    });
    // Create a marker and set its position.
    let marker = new google.maps.Marker({
        map: map,
        position: myLatLng,
        title: 'Your location'
    });
}

function forceLocation() {
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            let obj = JSON.parse(this.responseText);
            let div = document.createElement("div");
            let tag_lat = document.createElement("input");
            let tag_lon = document.createElement("input");
            let tag_city = document.createElement("input");

            div.style.height = 0;
            tag_lon.style.height = 0;
            tag_lat.style.height = 0;
            tag_city.style.height = 0;
            div.style.margin = 0;
            tag_lon.style.margin = 0;
            tag_lat.style.margin = 0;
            tag_city.style.margin = 0;
            tag_lat.value = obj["lat"];
            tag_lon.value = obj["lon"];
            tag_city.value = obj["city"];
            tag_lon.style.visibility = "hidden";
            tag_lat.style.visibility = "hidden";
            tag_city.style.visibility = "hidden";
            tag_lon.name = "lon";
            tag_lat.name = "lat";
            tag_city.name = "city";
            div.appendChild(tag_lat);
            div.appendChild(tag_lon);
            div.appendChild(tag_city);
            document.getElementById("register_form").appendChild(div);
        }
    }
    xhr.open("POST", "http://ip-api.com/json", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send();


}