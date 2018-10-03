$( window ).load(function () {
    $.getJSON($SCRIPT_ROOT + '/_get_pics', {}, function (data) {
        display_pics(data);
        if (data['pics'].length < 5) {
            add_pic();
        }
    });
});

function display_pics(data) {
    data['pics'].forEach(function (pic) {
        $('#gallery').append("<div class='col-md-4 thumbnail gallery_img'><img src='" + pic[2] + "' id='" + pic[0] + "'/></div>");
    });
    $('.gallery_img').on('click', function () {
        $('.gallery_img').removeClass('active');
        $(this).addClass('active');
    });
}

function add_pic() {
    $('#gallery_controls').append(
        `<form class="form-inline" action="/_upload" enctype=multipart/form-data method="POST">
            <div class="form-group">
                <input type="file" class="form-control-file" name="image_upload"/>
            </div>    
            <div class="form-group">
                <button class='btn btn-primary' type="submit">Upload</button>
            </div>
        </form>
`);
}

$('#delete_pic').on('click', function () {
    $.getJSON($SCRIPT_ROOT + '/_del_pics', {
        pic_id: $('.active').find('img').attr('id')
    }, function (data) {
        if (data['result'] === true){
            $('.active').remove();
        }
        else{
            alert('Could not delete this picture')
        }
    });
});

$('#set_pic').on('click', function () {
    $.getJSON($SCRIPT_ROOT + '/_set_profile_pic', {
        pic_id: $('.active').find('img').attr('id')
    }, function () {});
});