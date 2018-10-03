function get_ct() {
    $.getJSON($SCRIPT_ROOT + '/_get_notifs', {}, function (data) {
        if (data.ct > 0) {
            let notif_select =
                `<li class='dropdown notif'>
                    <div class='dropdown-toggle' id='dropdownMenuButton' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>
                        <span class='glyphicon glyphicon-bell'></span>
                        <span id='notif_ct' class='badge badge-secondary'>` + data.ct + `</span>
                    </div>
                    <ul class='dropdown-menu'>`;
            data.notifs.forEach(function (notif, idx) {
                notif_select += "<li class='dropdown-item notif-item' id='notif_" + notif[3] + "'> New " + notif[0] + " from <a href='/profile/" + notif[2] + "'>" + notif[2] + "</a><span class='glyphicon glyphicon-remove notif-close'></span></li>";
                if (idx < data.notifs.length - 1) {
                    notif_select += "<li role='separator' class='divider'></li>";
                }
            });
            notif_select = notif_select + "</ul>";
            $(".notif").html(notif_select);
            $(".notif").hover(function () {
                $(this).find('.dropdown-menu').stop(true, true).delay(100).fadeIn(500);
            }, function () {
                $(this).find('.dropdown-menu').stop(true, true).delay(100).fadeOut(500);
            });
            $(document).on('click', ".notif-close", function () {
                let current_notif = $(this).parent('.notif-item');
                if (current_notif.prev('.divider').attr('class') !== "divider") {
                    current_notif.next('.divider').remove();
                }
                else {
                    current_notif.prev('.divider').remove();
                }
                current_notif.remove();
                $.getJSON($SCRIPT_ROOT + '/_delete_notif', {
                    notif_id: current_notif.attr('id').slice(6)
                }, function () {
                    let ct = $('#notif_ct');
                    if (parseInt(ct.html()) <= 1) {
                        $('.notif').html("<span class='glyphicon glyphicon-bell'></span>");
                    }
                    else {
                        ct.html(parseInt(ct.html()) - 1);
                    }
                });
            });
        }
        else {
            $(".notif").html("<span class='glyphicon glyphicon-bell'></span>");
        }
    });
}

function get_connected() {
    $.getJSON($SCRIPT_ROOT + '/_get_connected', {}, function (data) {
        let connected = data.connected;
        let selector = "";

        $('.is_connected').remove();
        connected.forEach(function (user_id) {
            selector = '#usr_' + user_id;
            $("<div class='is_connected'></div>").insertAfter(selector);
        });

        $('.m-is_connected').remove();
        connected.forEach(function (user_id) {
            selector = '#m-usr_' + user_id;
            $("<div class='m-is_connected'></div>").insertAfter(selector);
        });

        $('.p-is_connected').remove();
        connected.forEach(function (user_id) {
            selector = '#p-usr_' + user_id;
            $("<div class='p-is_connected'></div>").insertAfter(selector);
        });

        $('.s-is_connected').remove();
        connected.forEach(function (user_id) {
            selector = '#s-usr_' + user_id;
            $("<div class='s-is_connected'></div>").insertAfter(selector);
        });
    });

}


function update_notifs() {
    setTimeout(function () {
        get_ct();
        get_connected();
        update_notifs();
    }, 7000);
}


get_ct();
get_connected();
update_notifs();