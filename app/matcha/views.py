from flask import render_template, request, flash, session, redirect, url_for, jsonify, redirect, Response
from flask_socketio import emit, join_room, leave_room
from werkzeug.security import generate_password_hash
from matcha import app, socketio
from matcha.db import db
from matcha.models import DBNode, User, Chat, Notif, Visit, Like, Hashtag, Pic
import json, requests
from functools import wraps
from matcha.utils import format_timestamp, time_delta, populate, age_to_date, date_to_age, allowed_file
import numpy as np
from math import degrees, radians, cos
from werkzeug.utils import secure_filename
import os


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'log' not in session or session['log'] == '':
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update')
@login_required
def update():
    user = User()
    info = json.loads(session['log'])
    user.dict_to_obj(info)
    return render_template('update.html', info=info)


@app.route('/profile/<username>')
@login_required
def other_profile(username):
    user = User()
    logged = json.loads(session['log'])
    my_id = logged['id']
    if not user.exists(username):
        return render_template('print.html', title='Error', values=['This user does not exist'])
    if username != logged['login']:
        vis = Visit(my_id)
        vis.add_visit(username)
    user.dict_to_obj(logged)
    session["log"] = user.to_json()
    logged = json.loads(session['log'])
    session["user_id"] = ''
    res = user.query('''SELECT users.id, login, gender, email, pic_id, popularity, firstname, lastname, longitude, latitude, bio, \
            orientation, birthdate, city FROM users
            WHERE login = ?''', (username,))
    profile_pic = user.query('''SELECT * FROM pics WHERE id = ?''', (res[0][4],))
    pics = user.query('''SELECT * FROM pics WHERE user_id = ? AND id != ?''', (res[0][0], res[0][4]))
    info = {'id': res[0][0], 'login': res[0][1], 'gender': res[0][2], 'email': res[0][3], 'pic_id': res[0][4],
            'popularity': res[0][5], 'firstname': res[0][6], 'lastname': res[0][7], 'longitude': res[0][8],
            'latitude': res[0][9], 'bio': res[0][10], 'orientation': res[0][11], "birthdate": res[0][12],
            "city": res[0][13], "pics": pics, "likes": user.does_like(my_id, username),
            "blocks": user.does_block(my_id, username)}
    if len(profile_pic) > 0:
        info.update({'profile_pic': profile_pic[0]})
    return render_template('profil.html', info=info, user=logged)


@app.route('/reports')
@login_required
def reports():
    if DBNode.query('''SELECT admin FROM users WHERE id = ?''', (json.loads(session['log'])['id'],))[0][0] == 1:
        res = DBNode.query('''
          SELECT COUNT(*), users.id, users.login FROM reports
          INNER JOIN users on users.id = to_id 
          GROUP BY users.id''', ())
        return render_template('reports.html', reports=res)
    else:
        return render_template('print.html', title='Access Denied', values=['You don\'t have access to this page'])


@app.route('/populate')
@login_required
def populate_view():
    if DBNode.query('''SELECT admin FROM users WHERE id = ?''', (json.loads(session['log'])['id'],))[0][0] == 1:
        return render_template('populate.html')
    else:
        return render_template('print.html', title='Access Denied', values=['You don\'t have access to this page'])


@app.route('/profile')
@login_required
def profile():
    user = User()
    info = json.loads(session['log'])
    user.dict_to_obj(info)
    session['log'] = user.to_json()
    info = json.loads(session['log'])
    profile_pic = user.query('''SELECT * FROM pics WHERE id = ?''', (info['pic_id'],))
    pics = user.query('''SELECT * FROM pics WHERE user_id = ? AND id != ?''', (info['id'], info['pic_id']))
    info['pics'] = pics
    if len(profile_pic) > 0:
        info['profile_pic'] = profile_pic[0]
    return render_template('profil.html', info=info)


@app.route('/_delete_profile')
def delete_profile():
    user_id = request.args.get('id')
    log = json.loads(session['log'])
    if log['id'] == user_id or log['admin'] == 1:
        us = User()
        us.delete(user_id)
    return jsonify()


@app.route('/_block')
def block_user():
    us = User()
    user_id = request.args.get('id')
    info = json.loads(session['log'])
    res = False
    ct = us.count_query('''DELETE FROM blocks WHERE to_id = ? AND from_id = ?''', (user_id, info['id']))
    if ct == 0:
        res = True
        us.query('''INSERT INTO blocks(to_id, from_id) VALUES(?, ?)''', (user_id, info['id']))
    return jsonify(result=res)


@app.route('/_report')
def report_user():
    us = User()
    user_id = request.args.get('id')
    info = json.loads(session['log'])
    ct = us.count_query('''DELETE FROM reports WHERE to_id = ? AND from_id = ?''', (user_id, info['id']))
    if ct == 0:
        us.query('''INSERT INTO reports(to_id, from_id) VALUES(?, ?)''', (user_id, info['id']))
    return jsonify(result=[])


@app.route('/_get_notifs')
def get_notif():
    notif_inst = Notif(json.loads(session['log'])['id'])
    ct = notif_inst.count()
    notifs = notif_inst.get_all()
    if len(ct) > 0:
        return jsonify(ct=ct[0][0], notifs=notifs)
    return jsonify(ct=0, notifs=notifs)


@app.route('/reset')
@login_required
def setup_database():
    if DBNode.query('''SELECT admin FROM users WHERE id = ?''', (json.loads(session['log'])['id'],))[0][0] == 1:
        db.init_db()
        return render_template('print.html', title="Database Reset", values=["The database was resetted"])
    else:
        return render_template('print.html', title='Access Denied', values=['You don\'t have access to this page'])


@app.route('/login')
def login():
    return render_template('login.html')


# Create a jinja filter for converting timestamp to date
@app.template_filter('ctime')
def time_format(s):
    return time_delta(s)


# Create a jinja filter for calculating age from date
@app.template_filter('age')
def get_age(s):
    return date_to_age(s)


# Create a jinja filter for extracting session['log'] admin status
@app.template_filter('is_admin')
def is_admin(s):
    return json.loads(s)['admin'] == 1


@app.route('/matches')
@login_required
def matches():
    user = User()
    user_matches = user.matched(json.loads(session['log'])['id'])
    user_likes = user.likes(json.loads(session['log'])['id'])
    my_likes = user.my_likes(json.loads(session['log'])['id'])
    arr_match = np.array(user_matches)
    if len(arr_match) > 0:
        user_likes = [likes for likes in user_likes if str(likes[2]) not in arr_match[:, 2]]
        my_likes = [likes for likes in my_likes if str(likes[2]) not in arr_match[:, 2]]
    vis = Visit(json.loads(session['log'])['id'])
    visits = vis.get_all()
    return render_template('matches.html', matches=user_matches, likes=user_likes, my_likes=my_likes, visits=visits)


@app.route('/logout')
@login_required
def logout():
    user = User()
    user.logout(json.loads(session['log'])['id'])
    session['log'] = ''
    return redirect(url_for('login'))


@app.route('/login/validation', methods=['POST'])
def login_validation():
    user = User()
    validity = user.auth(request.form['login'], request.form['password'])
    if validity:
        session['log'] = user.to_json()
        return redirect(url_for('chat'))
    else:
        return render_template('print.html', title="Login error",
                               values=["An error occurred during your login attempt."])


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/confirm/<token>')
def confirm_email(token):
    us = User()
    try:
        us.confirm_token(token)
    except:
        return render_template('print.html', title='Wrong token', values=['Your email could not be confirmed'])
    return render_template('print.html', title='Account confirmed', values=['Your account has been confirmed'])


@app.route('/register/check_input', methods=['POST'])
def register_check_input():
    user = User()
    user.dict_to_obj(request.form)
    error = user.check_password()
    error.update(user.check_username())
    error.update(user.check_email())
    liste = list()
    if True in error.values():
        for key, value in error.items():
            if value is True:
                liste.append(key)
    else:
        user.register()
        liste.append("You were successfully registered.")
        liste.append("An email was sent for account confirmation.")
    return render_template('print.html', title="User Creation", values=liste)


@app.route('/register/validation', methods=['POST'])
def register_validation():
    new_user = User()
    hashed = generate_password_hash(request.form['password'])
    new_user.register((request.form['login'], request.form['firstname'], request.form['lastname'],
                       request.form['email'], hashed, request.form['gender']))
    return render_template('print.html', title="User Creation", values=["Your account was successfully created"])


@app.route('/chat')
@login_required
def chat():
    user = User()
    user_matches = user.matched(json.loads(session['log'])['id'])
    return render_template('chat.html', matches=user_matches)


@app.route('/forgot_password')
def forgot_pass():
    return render_template('password_recovery.html')


@app.route('/_recovery', methods=['POST'])
def recovery():
    us = User()
    us.password_recovery(request.form['email'])
    return render_template('print.html', title='Password',
                           values=["A new password has been set to your address"])


@app.route('/search')
@login_required
def searching():
    user = User()
    logs = json.loads(session['log'])
    if user.is_complete(logs['id']):
        return render_template('search.html')
    else:
        return render_template('print.html', title="Profile incomplete", values=["Please complete your profile"])


@app.route('/_search_user')
def search_user():
    lat = float(json.loads(session['log'])['latitude'])
    lng = float(json.loads(session['log'])['longitude'])
    dist = float(request.args.get('distance'))
    minlat = lat - degrees(dist / 6371)
    maxlat = lat + degrees(dist / 6371)
    minlng = lng - degrees(dist / 6371 / cos(radians(lat)))
    maxlng = lng + degrees(dist / 6371 / cos(radians(lat)))
    data = {
        'login': request.args.get('login'),
        'popularity': [request.args.get('min_popularity'), request.args.get('max_popularity')],
        'age': age_to_date(request.args.get('min_age'), request.args.get('max_age')),
        'distance': [minlat, maxlat, minlng, maxlng],
        'radius': dist,
        'sort': request.args.get('sort').lower(),
        'location': [lat, lng],
        'matching': request.args.get('matching'),
        'hashtag': request.args.getlist('hashtag[]')
    }
    user = User()
    res = user.search(data, json.loads(session['log'])['id'])
    return jsonify(result=res, debug=data)


@app.route('/_populate')
def populate_db():
    nb = 550
    result = populate(nb).json()
    user = User()
    ret = []
    for res in result['results']:
        ret.append(user.populate(res))
    vis = Visit(0)
    vis.random(6 * nb)
    lik = Like()
    lik.random(6 * nb)
    hash = Hashtag()
    hash.random(3 * nb)
    return jsonify(result=ret)


@app.route('/_get_message')
@login_required
def get_messages():
    current_id = json.loads(session['log'])['id']
    chat_user_id = request.args.get('target_user_id')
    chat_socket = Chat(current_id, chat_user_id)
    messages = chat_socket.get()
    notif_inst = Notif(current_id)
    notif_inst.flush(chat_user_id, 'message')
    messages = format_timestamp(messages, current_id)
    user = User()
    if len(messages) > 0 and user.is_matched(current_id, chat_user_id):
        return jsonify(result=messages)
    return jsonify(result=[])


@app.route('/_treatlocation', methods=['POST'])
def treatlocation():
    user = User()
    info = json.loads(session['log'])
    user.dict_to_obj(info)
    longitude = request.form['longitude']
    latitude = request.form['latitude']
    response = requests.get("https://nominatim.openstreetmap.org/reverse?format=json&zoom=10&" +
                            "lat=" + latitude + "&lon=" + longitude)
    result = response.json()
    city = result["address"]["city"]
    user.updatelocation(longitude, latitude)
    user.update_city(city)
    return ""


@app.route('/_like')
def switch_like():
    lik = Like()
    ret = lik.switch(json.loads(session['log'])['id'], request.args.get('user_profile'))
    return jsonify(likes=ret)


# Methods that handle hashtags
@app.route('/_get_hashtags')
def get_hashtags():
    user = User()
    if 'login' not in request.args:
        info = json.loads(session['log'])
        user.dict_to_obj(info)
    else:
        user.dict_to_obj({'id': request.args.get('login')})
    val = user.get_hashtags()
    val = json.dumps(val)
    return val


@app.route('/update_pics')
def update_pics():
    return render_template('update_pics.html', error_message='')


@app.route('/_get_pics')
def get_pics():
    user = User()
    val = user.get_pics(json.loads(session['log'])['id'])
    return jsonify(pics=val)


@app.route('/_del_pics')
def del_pics():
    user = User()
    val = user.del_pics(json.loads(session['log'])['id'], request.args.get('pic_id'))
    return jsonify(result=val)


@app.route('/_set_profile_pic')
def set_profile_pic():
    user = User()
    val = user.set_profile_pic(json.loads(session['log'])['id'], request.args.get('pic_id'))
    return jsonify(pics=val)


@app.route('/_upload', methods=['GET', 'POST'])
def upload_pics():
    if request.method == 'POST':
        if 'image_upload' not in request.files:
            return render_template("update_pics.html", error_message='Please select a file')
        file = request.files['image_upload']
        if file.filename == '':
            return redirect(url_for('update_pics'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('matcha/static/assets/pics/', filename))
            pic = Pic()
            pic.set(filename, json.loads(session['log'])['id'])
            return redirect(url_for('update_pics'))
    return render_template("update_pics.html", error_message='Please select a valid file')


# Methods that handle hashtags
@app.route('/_get_hashtag_list')
def get_all_hashtags():
    hash_obj = Hashtag()
    val = hash_obj.get_distinct()
    return jsonify(tag_list=val)


@app.route('/_add_hashtag', methods=['POST'])
def add_hashtag():
    user = User()
    info = json.loads(session['log'])
    user.dict_to_obj(info)
    my_hash = request.form['hashtag']
    user.add_hashtag(my_hash)
    return jsonify(result=[])


@app.route('/_delete_hashtag', methods=['POST'])
def delete_hashtag():
    user = User()
    info = json.loads(session['log'])
    user.dict_to_obj(info)
    my_hash = request.form['hashtag']
    user.delete_hashtag(my_hash)
    return jsonify(result=[])


# Method that handle user update
@app.route('/_update/<var>', methods=['POST'])
def login_update(var):
    user = User()
    info = json.loads(session['log'])
    user.dict_to_obj(info)
    if var == "login":
        user.login = request.form['login']
        message = user.update_login()
    elif var == "firstname":
        user.firstname = request.form["firstname"]
        message = user.update_firstname()
    elif var == "lastname":
        user.lastname = request.form['lastname']
        message = user.update_lastname()
    elif var == "password":
        user.oldpassword = request.form['oldpassword']
        user.password = request.form['password']
        user.repeatpassword = request.form['repeatpassword']
        message = user.update_password()
    elif var == "email":
        user.email = request.form['email']
        message = user.update_email()
    elif var == "gender":
        user.gender = request.form['gender']
        message = user.update_gender()
    elif var == "orientation":
        user.orientation = request.form['orientation']
        message = user.update_orientation()
    elif var == "bio":
        user.bio = request.form['bio']
        message = user.update_bio()
    elif var == "birthdate":
        user.birthdate = request.form['birthdate']
        message = user.update_birthdate()
    else:
        message = ''
        session['log'] = user.to_json()
    return message


@app.route('/_get_connected')
def get_connected():
    user = User()
    connected_users = user.get_connected()
    if len(connected_users) > 0:
        return jsonify(connected=connected_users)
    return jsonify(connected=[])


@app.route('/_set_connected')
def set_connected():
    user = User()
    if session['log'] and session['log'] != '':
        status = request.args.get('status')
        user.set_connected(json.loads(session['log'])['id'], int(status))
        return jsonify(result=[True])
    return jsonify(result=[False])


@app.route('/_delete_notif')
def delete_notif():
    notif = Notif(json.loads(session['log'])['id'])
    my_notif = request.args.get('notif_id')
    notif.delete(my_notif)
    return jsonify(result=[])


@socketio.on('join_private')
@login_required
def join_private(room):
    current_id = json.loads(session['log'])['id']
    chat_socket = Chat(current_id, int(room['rec_user_id']))
    private_room = chat_socket.get_room()
    join_room(private_room)


@socketio.on('connect')
@login_required
def store_socket():
    current_id = json.loads(session['log'])['id']
    socket_id = request.sid
    user = User()
    user.update_socket(current_id, socket_id)


@socketio.on('disconnect')
@login_required
def store_socket():
    current_id = json.loads(session['log'])['id']
    user = User()
    user.update_socket(current_id, '')


@socketio.on('mess_sent')
@login_required
def handle_mess(msg):
    send_user_id = json.loads(session['log'])['id']
    user = User()
    if not user.is_matched(send_user_id, msg['rec_user_id']):
        return
    chat_socket = Chat(send_user_id, msg['rec_user_id'])
    chat_socket.send(msg['message'])
    private_room = chat_socket.get_room()
    socketio.emit('mess_received', msg, room=private_room)
    notif_inst = Notif(send_user_id)
    notif_inst.send(msg['rec_user_id'], 'message')
