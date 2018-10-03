$('.delete_profile').on('click', function () {
    let delete_id = $(this).attr('id');
    $.getJSON($SCRIPT_ROOT + '/_delete_profile', {
            id: $(this).attr('id')
        }, function () {
            $('#' + delete_id).closest('.row').remove();
        }
    )
});