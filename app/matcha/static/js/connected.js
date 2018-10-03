$( window ).load(function() {
    $.getJSON($SCRIPT_ROOT + '/_set_connected', {
        status: 1
    }, function () {
    });
});

$( window ).on('beforeunload', function() {
    $.getJSON($SCRIPT_ROOT + '/_set_connected', {
        status: 0
    }, function () {});
});

