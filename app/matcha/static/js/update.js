let error = 0;

function update(button_id, values, url) {
    let button = document.getElementById(button_id);
    button.addEventListener("click", function () {
        let string = "";
        for (i = 0; i < values.length; i++) {
            let input = document.getElementById(values[i]).value;
            if (input === "") {
                document.getElementById(values[i]).placeholder = "This field shouldn't be empty!";
                let error = 1;
            }
            if (i < values.length - 1) {
                string = string + values[i] + '=' + input + '&';
            }
            else {
                string = string + values[i] + '=' + input;
            }
        }
        if (error !== 1) {
            let xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function () {
                if (this.readyState === 4 && this.status === 200) {
                    $('#alert_box').fadeIn();
                    $('#alert_box').removeClass('hide');
                    $('#alert_message').html(this.responseText);
                }
            };
            xhr.open('POST', url, true);
            xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhr.send(string);
        }
    });
}

let tag_list;
$.getJSON($SCRIPT_ROOT + '/_get_hashtag_list', {}, function (data) {
    tag_list = data['tag_list'];
    $('#new_hashtag').autocomplete({source: tag_list});
});

update("login_update", ["login"], "_update/login");
update("firstname_update", ["firstname"], "_update/firstname");
update("lastname_update", ["lastname"], "_update/lastname");
update("password_update", ["oldpassword", "password", "repeatpassword"], "_update/password");
update("email_update", ["email"], "_update/email");
update("gender_update", ["gender"], "_update/gender");
update("orientation_update", ["orientation"], "_update/orientation");
update("bio_update", ["bio"], "_update/bio");
update("birthdate_update", ["birthdate"], "_update/birthdate");
