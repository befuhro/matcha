$('.like_btn').on('click', function () {
    $.getJSON($SCRIPT_ROOT + '/_like', {
        user_profile: $('.like_btn').attr('id')
    }, function (data) {
        let like_btn = $('.like_btn');
        if (data['likes'] === true) {
            like_btn.addClass('btn-warning');
            like_btn.removeClass('btn-danger');
            like_btn.html('Unlike <span class="glyphicon glyphicon-heart"></span>')
        }
        else {
            like_btn.removeClass('btn-warning');
            like_btn.addClass('btn-danger');
            like_btn.html('Like <span class="glyphicon glyphicon-heart"></span>')
        }
    });
});

$('.block').on('click', function(){
    $.getJSON($SCRIPT_ROOT + '/_block', {
        id: $(this).attr('id')
    }, function(data){
        if (data.result === false)
            $('.block').html('<span class="glyphicon glyphicon-sunglasses"></span> Block');
        else
            $('.block').html('<del><span class="glyphicon glyphicon-sunglasses"></span> Block</del>');
    });
});

$('.report').on('click', function(){
    $.getJSON($SCRIPT_ROOT + '/_report', {
        id: $(this).attr('id')
    }, function(){
    });
    $(this).html('Reported!');
});

