let socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function () {
    document.getElementById('chat_form').addEventListener('submit', function (e) {
        if ($('.contact_thumb-selected').attr('id')) {
            e.preventDefault();
            let user_input = $("#message").val();
            $("#message").val('');
            if (user_input !== '')
                append_msg(1, user_input, 0);
            if (user_input !== '') {
                socket.emit('mess_sent', {
                    message: user_input,
                    rec_user_id: $('.contact_thumb-selected').attr('id').slice(4),
                });
            }
        }
    });
});

socket.on('mess_received', function (msg) {
    if (msg.rec_user_id !== $('.contact_thumb-selected').attr('id').slice(4))
        append_msg(0, msg.message, 0);
});


function append_msg(mine, msg, time) {
    let newrow = document.createElement('div');
    newrow.className = 'row rounded';
    let add_msg = document.createElement('div');
    if (mine === 1)
        add_msg.className = "chat_msg my_msg";
    else
        add_msg.className = "chat_msg";
    add_msg.innerHTML = msg;
    newrow.append(add_msg);
    let timestamp = document.createElement('div');
    timestamp.className = "timestamp";
    if (mine===1)
        timestamp.className = "timestamp my_timestamp";
    timestamp.innerText = '';
    if (time !== '' && time !== 0 && time)
        timestamp.innerText = time;
    let cont = document.getElementById('mess_container');
    cont.append(timestamp);
    cont.append(newrow);
    cont.scrollTop = cont.scrollHeight;
}

function add_contact(pic) {
    $("#contacts").append("<div class='contact'><img class='contact_thumb' src='" + pic + "'/></div>");
}


$(".contact_thumb").on('click', function () {
    socket.emit('join_private', {
        rec_user_id: $(this).attr('id').slice(4)
    });
    $("#chat_form").removeClass('invisible');
    $("#mess_container").empty();
    $(".contact_thumb").removeClass('contact_thumb-selected');
    $(this).addClass("contact_thumb-selected");
    $.getJSON($SCRIPT_ROOT + '/_get_message', {
        target_user_id: $(this).attr('id').slice(4)
    }, function (data) {
        data.result.forEach(function (msg) {
            append_msg(msg[0], msg[1], msg[2]);
        });
    });
});