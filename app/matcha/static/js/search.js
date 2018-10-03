$( window ).load(function () {
    $('.search_row').append('<div class="loader"></div>');
    $.getJSON($SCRIPT_ROOT + '/_search_user', {
        login: '',
        distance: 200,
        min_age: 18,
        max_age: 100,
        min_popularity: 0,
        max_popularity: 100,
        sort: 'distance',
        hashtag: []
    }, function (data) {
        display_results(data);
        $('.loader').remove();
    });
});


$('#search_submit').on('click', function () {
    $('.search_row').append('<div class="loader"></div>');
    $('.col-xs-12').remove();
    $.getJSON($SCRIPT_ROOT + '/_search_user', {
        login: $('#search_input').val(),
        distance: $("#distance_slider-range").slider("values", 0),
        min_age: $("#ageslider-range").slider("values", 0),
        max_age: $("#ageslider-range").slider("values", 1),
        min_popularity: $("#popslider-range").slider("values", 0),
        max_popularity: $("#popslider-range").slider("values", 1),
        hashtag: $('.hash').text().split('×').slice(0, -1),
        sort: $('#sortby').val(),
        matching: $('#match_me').is(':checked')
    }, function (data) {
        display_results(data);
        $('.loader').remove();
    });
});

function display_results(data) {
    data.result.forEach(function (user) {
        $('.search_list').append(
            `<div class="col-xs-12 col-sm-6 col-md-4 col-lg-3 col-xl-2">
                <div class='search_item'>
                    <div>
                        <a href="/profile/` + user[0] + `"><img id='s-usr_` + user[9] + `' src="` + user[3] + `"/></a>
                    </div>
                    <div class="search_info">
                        <div class="search_login">
                            <span>` + user[0].substring(0, 16) + `</span>
                        </div>
                        <div class="search_age">
                            <span>` + calculateAge(user[2]) + `</span><br/>
                            <span> ` + user[4].substring(0, 16) + `</span>
                        </div>
                     </div>
                  </div>
             </div>`);
    });
}

function calculateAge(birthday) {
    let dob = new Date(birthday);
    let diff = Date.now() - dob.getTime();
    let age_dt = new Date(diff);
    return Math.abs(age_dt.getUTCFullYear() - 1970);
}

$(function () {
    $("#popslider-range").slider({
        range: true,
        min: 0,
        max: 100,
        values: [0, 100],
        slide: function (event, ui) {
            $("#pop_slider").val(ui.values[0] + " - " + ui.values[1]);
        }
    });
    $("#pop_slider").val($("#popslider-range").slider("values", 0) +
        " - " + $("#popslider-range").slider("values", 1));


    $("#ageslider-range").slider({
        range: true,
        min: 18,
        max: 100,
        values: [18, 100],
        slide: function (event, ui) {
            $("#age_slider").val(ui.values[0] + " - " + ui.values[1]);
        }
    });
    $("#age_slider").val($("#ageslider-range").slider("values", 0) +
        " - " + $("#ageslider-range").slider("values", 1));

    $("#distance_slider-range").slider({
        min: 0,
        max: 200,
        value: 200,
        slide: function (event, ui) {
            $("#distance_slider").val(ui.value + ' km');
        }
    });
    $("#distance_slider").val($("#distance_slider-range").slider("value").toString() + ' km');
});


let tag_list;
$.getJSON($SCRIPT_ROOT + '/_get_hashtag_list', {}, function (data) {
    tag_list = data['tag_list'];
    $('#hash_input').autocomplete({source: tag_list});
});

$('#hash_submit').on('click', function () {
    if ($.inArray($('#hash_input').val(), tag_list) !== -1) {
        $('#hash_list').append("<span class='hash'>" + $('#hash_input').val() + "<span class='close'>&times</span></span>");
        $('#hash_input').val('');
        $('.close').on('click', function () {
            $(this).parent().remove();
        });
    }
});
