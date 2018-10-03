//get hashtags from database
function get_hashtags() {
    $.getJSON('/_get_hashtags', function (data) {
        for (let i = 0; i < data.length; i++) {
            let hashtags = document.getElementById("hashtags");
            let index = i.toString();
            let hash = document.createElement('div');
            hash.className = "hash";
            hash.innerHTML = data[i];

            let close = document.createElement('div');
            close.className = "close";
            close.innerHTML = "&times";
            close.id = index;
            //function that delete hashtag from page and database on click.
            close.onclick = function () {
                string = document.getElementById(this.id).parentElement.innerText;
                string = string.slice(0, string.length - 1);
                document.getElementById(this.id).parentElement.remove();
                let xhr = new XMLHttpRequest();
                xhr.open('POST', '/_delete_hashtag', true);
                xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xhr.send("hashtag=" + string);
            };
            hash.appendChild(close);
            hashtags.appendChild(hash);
        }
    })
}

//handle and add new hashtag put it on page and to database.
function new_hashtag() {
    document.getElementById("add_button").onclick = function () {
        let text = document.getElementById('new_hashtag').value;
        document.getElementById('new_hashtag').value = "";
        let hashtags = document.getElementById("hashtags");
        let list = hashtags.children;
        //check for double.
        for (let i = 0; i < list.length; i++) {
            let text_hash = list[i].textContent;
            text_hash = text_hash.slice(0, text_hash.length - 1);
            if (text_hash === text) {
                $('#alert_box').fadeIn();
                $('#alert_box').removeClass('hide');
                $('#alert_message').html("You already have this interest");
                return false;
            }
        }
        //check if hashtag is empty.
        if (!text.match(/^[0-9a-z]+$/)) {
            $('#alert_box').fadeIn();
            $('#alert_box').removeClass('hide');
            $('#alert_message').html("Please type a valid interest");
            return false;
        }

        let hash = document.createElement('div');
        hash.className = "hash";
        hash.innerHTML = text;

        let close = document.createElement("div");
        close.className = "close";
        close.innerHTML = "&times";
        if (hashtags.lastChild) {
            close.id = (Number(hashtags.lastChild.lastChild.id) + 1).toString();
        }
        else {
            close.id = '0';
        }
        //function that delete hashtag from page and database on click.
        close.onclick = function () {
            let this_str = document.getElementById(this.id).parentElement.innerText;
            this_str = string.slice(0, this_str.length - 1);
            document.getElementById(this.id).parentElement.remove();
            let xhr = new XMLHttpRequest();
            xhr.open('POST', '/_delete_hashtag', true);
            xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhr.send("hashtag=" + this_str);
        };
        hash.appendChild(close);
        hashtags.appendChild(hash);
        let xhr = new XMLHttpRequest();
        xhr.open('POST', '/_add_hashtag', true);
        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhr.send("hashtag=" + text);
        $('#alert_box').addClass('hide');
        return false;
    };
}

//display hashtags into div.
function display_hashtags(user_id) {
    $.getJSON('/_get_hashtags', {
        login: user_id
    }, function (data) {
        for (let i = 0; i < data.length; i++) {
            let hashtags = document.getElementById("hashtags");
            let hash = document.createElement('div');
            hash.className = "hash";
            hash.innerHTML = data[i];
            hashtags.appendChild(hash);
        }
        if (data.length === 0) {
            $('#hashtags').parent().remove();
        }
    })
}