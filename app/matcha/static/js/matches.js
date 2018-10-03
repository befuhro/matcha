$('.match_category .btn').on('click', function(){
    $('.match_subtitle').addClass('hide');
    $('#sub-' + $(this).attr('id').slice(3)).removeClass('hide');
    $('.match_list').addClass('hide');
    $('#list-' + $(this).attr('id').slice(4)).removeClass('hide');
});