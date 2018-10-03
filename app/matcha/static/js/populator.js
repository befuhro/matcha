$('#populate_btn').on('click', function () {
    $('.loader').removeClass('hide');
    $('#populate_btn').remove();
    $.getJSON($SCRIPT_ROOT + '/_populate', {
        }, function (data) {
            $('.loader').addClass('hide');
            let al = $('.alert');
            al.removeClass('alert-info');
            al.addClass('alert-success');
            al.html('The database is now plenty of fake users!');
            display_results(data);
        }
    )
});

function display_results(data) {
    data.result.forEach(function (user) {
        $('.search_list').append(
            `<div class="col-xs-12 col-sm-6 col-md-4 col-lg-3 col-xl-2">
                <div class='search_item'>
                    <div>
                        <a href="/profile/` + user[0] + `"><img src="` + user[11] + `"/></a>
                    </div>
                    <div class="search_info">
                        <div class="search_login">
                            <span>` + user[0] + `</span>
                        </div>
                     </div>
                  </div>
             </div>`);
    });
}