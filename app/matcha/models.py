from matcha import app
import sqlite3 as sqlite
from werkzeug.security import check_password_hash, generate_password_hash
import re
import json
import datetime
from matcha.utils import random_date, random_text, distance_sort, distance_filter, get_distance
import requests
from numpy import average
from itsdangerous import URLSafeTimedSerializer
from flask import render_template
import random
import string
from matcha.private import MAIL_SETUP
from email.message import EmailMessage
import smtplib

"""
This file contains every Database related classes
"""


# This class handles SQLite connections and queries

class DBNode:
    def __init__(self):
        print("connection initialized")

    @staticmethod
    def query(query, data_tuple):
        conn = sqlite.connect('/data/matcha.sqlite')
        c = conn.cursor()
        c.execute(query, data_tuple)
        conn.commit()
        result = c.fetchall()
        conn.close()
        return result

    @staticmethod
    def multiple_query(query, data_tuple):
        conn = sqlite.connect('/data/matcha.sqlite')
        c = conn.cursor()
        c.executemany(query, data_tuple)
        conn.commit()
        result = c.fetchall()
        conn.close()
        return result

    @staticmethod
    def count_query(query, data_tuple):
        conn = sqlite.connect('/data/matcha.sqlite')
        c = conn.cursor()
        c.execute(query, data_tuple)
        conn.commit()
        result = c.rowcount
        conn.close()
        return result


# This class handles Users

class User(DBNode):
    user_id = None
    login = None
    firstname = None
    lastname = None
    oldpassword = None
    password = None
    repeatpassword = None
    orientation = None
    bio = None
    email = None
    gender = None
    birthdate = None
    city = None
    lat = None
    lon = None
    admin = 0

    def __init__(self):
        super(User, self).__init__()
        print("user initialized")

    # Add data from a dict to object attributes
    def dict_to_obj(self, data):
        if 'id' in data and data['id'] != '':
            self.user_id = data['id']
        if 'login' in data and data['login'] != '':
            self.login = data['login']
        if 'firstname' in data and data['firstname'] != '':
            self.firstname = data['firstname']
        if 'lastname' in data and data['lastname'] != '':
            self.lastname = data['lastname']
        if 'password' in data and data['password'] != '':
            self.password = data['password']
        if 'repeatpassword' in data and data['repeatpassword'] != '':
            self.repeatpassword = data['repeatpassword']
        if 'oldpassword' in data and data['oldpassword'] != '':
            self.repeatpassword = data['oldpassword']
        if 'orientation' in data and data['orientation'] != '':
            self.orientation = data['orientation']
        if 'bio' in data and data['bio'] != '':
            self.bio = data['bio']
        if 'email' in data and data['email'] != '':
            self.email = data['email']
        if 'gender' in data and data['gender'] != '':
            self.gender = data['gender']
        if 'city' in data and data['city'] != '':
            self.city = data['city']
        if 'lat' in data and data['lat'] != '':
            self.lat = data['lat']
        if 'lon' in data and data['lon'] != '':
            self.lon = data['lon']

    def login_to_id(self, login):
        res = self.query('''
        SELECT id FROM users WHERE login=?
        ''', (login,))
        self.user_id = res[0][0]

    # Many methods that check input from user
    def check_password(self):
        match_error = self.password != self.repeatpassword
        length_error = self.password is None or len(self.password) < 8
        digit_error = length_error or re.search(r"\d", self.password) is None
        alphabetical_error = length_error or re.search(r"[A-Za-z]", self.password) is None
        symbol_error = length_error or re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', self.password) is None
        return {
            'Passwords do not match': match_error,
            'Passwords must contain at least 8 characters': length_error,
            'Passwords must contain at least one number': digit_error,
            'Passwords must contain at least a letter': alphabetical_error,
            'Passwords must contain at least a special character': symbol_error
        }

    def check_old_password(self):
        if self.oldpassword and self.auth(self.login, self.oldpassword) is False:
            return {'Initial password is wrong': True}
        return {'Initial password is wrong': False}

    def check_username(self):
        length_error = self.login is None or len(self.login) < 3
        res = self.query('''SELECT login FROM users WHERE login=?''', (self.login,))
        already_taken = False
        alnum_error = False
        if res:
            already_taken = True
        if not self.login.isalnum():
            alnum_error = True
        return {
            'A username must contain at least 3 characters': length_error,
            'This username is already taken': already_taken,
            'A username must not contain symbols': alnum_error
        }

    def check_email(self):
        parse_error = self.email is None or re.match(
            '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
            self.email) is None
        res = self.query('''SELECT COUNT(*) FROM users WHERE email=?''', (self.email,))
        if res[0][0] == 0:
            already_taken = False
        else:
            already_taken = True
        return {
            'This email adress is invalid': parse_error,
            'This email is already registered in our database': already_taken
        }

    # Insert value of object to database
    def register(self):
        hashed = generate_password_hash(self.password)
        self.query('''INSERT INTO users(login, firstname, lastname, email, password, gender, latitude, longitude, city) 
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (self.login, self.firstname, self.lastname, self.email, hashed, self.gender, self.lat, self.lon, self.city))
        self.generate_token(self.email)

    @staticmethod
    def send_email(email, content):
        msg = EmailMessage()
        msg.set_content(content)
        msg["Subject"] = "Matcha"
        msg["From"] = MAIL_SETUP["email"]
        msg["To"] = email
        s = smtplib.SMTP(MAIL_SETUP['smtp'], MAIL_SETUP["port"])
        s.starttls()
        s.login(MAIL_SETUP["email"], MAIL_SETUP["password"])
        try:
            s.send_message(msg)
        except:
            return False
        s.quit()
        return True

    @staticmethod
    def generate_token(email):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        url = "http://localhost:5000/confirm/" + serializer.dumps(email, salt='I_THINK_SO_I_SECURE')
        User.send_email(email, render_template('activate.html', confirm_url=url))
        return True

    def confirm_token(self, token, expiration=3600):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='I_THINK_SO_I_SECURE', max_age=expiration)
        res = self.query('''SELECT COUNT(*) FROM users WHERE email = ? and confirmed == '0' ''', (email,))
        if res[0][0] > 0:
            self.query('''UPDATE users SET confirmed = '1' WHERE email = ?''', (email,))
            return email
        else:
            return False

    # Methods that manage hashtag
    def get_hashtags(self):
        res = self.query('''SELECT hashtag FROM hashtags WHERE user_id = ?''', (self.user_id,))
        liste = list()
        for elt in res:
            liste.append(elt[0])
        return liste

    def delete_hashtag(self, hashtag):
        hashtag = hashtag.replace('\n', '')
        self.query('''DELETE FROM hashtags WHERE hashtag=? AND user_id=?''', (hashtag, self.user_id))

    def add_hashtag(self, hashtag):
        hashtag = hashtag.replace('\n', '')
        self.query('''INSERT INTO hashtags(user_id, hashtag) VALUES(?, ?)''', (self.user_id, hashtag))

    # Methods that update information of a user
    def updatelocation(self, longitude, latitude):
        self.query('''UPDATE users set longitude = (?), latitude = (?)  WHERE id = (?)''',
                   (longitude, latitude, self.user_id))

    def update_city(self, city):
        self.query('''UPDATE users set city = (?)  WHERE id = (?)''', (city, self.user_id))

    def update_login(self):
        error = self.check_username()
        message = str()
        if True in error.values():
            for key, value in error.items():
                if value is True:
                    message += key + '\n'
        else:
            self.query('''UPDATE users set login = (?) WHERE id = (?)''', (self.login, self.user_id))
            message = "Your login has been updated."
        return message

    def update_firstname(self):
        if len(self.firstname) < 2:
            return "Your firstname should contain at least 2 characters."
        elif not self.firstname.replace(' ', '').isalnum():
            return "Your firstname must not contain symbols"
        else:
            self.query('''UPDATE users set firstname = (?) WHERE id = (?)''', (self.firstname, self.user_id))
            return "Your firstname has been updated."

    def update_lastname(self):
        if len(self.lastname) < 2:
            return "Your lastname should contain at least 2 characters."
        elif not self.lastname.replace(' ', '').isalnum():
            return "Your lastname must not contain symbols"
        else:
            self.query('''UPDATE users set lastname = (?) WHERE id = (?)''', (self.lastname, self.user_id))
            return "Your lastname has been updated."

    def update_password(self):
        error = self.check_password()
        res = self.query('''SELECT password FROM users WHERE id = ?''', (self.user_id,))
        if len(res) > 0 and check_password_hash(res[0][0], self.oldpassword) is False:
            error["Your password doesn't match with the one in database"] = True
        message = str()
        if True in error.values():
            for key, value in error.items():
                if value is True:
                    message += key + '\n'
        else:
            hashed = generate_password_hash(self.password)
            self.query('''UPDATE users set password = (?) WHERE id = (?)''', (hashed, self.user_id))
            message = "Your password has been updated."
        return message

    def update_email(self):
        error = self.check_email()
        message = str()
        if True in error.values():
            for key, value in error.items():
                if value is True:
                    message += key + '\n'
        else:
            self.query('''UPDATE users set email = (?) WHERE id = (?)''', (self.email, self.user_id))
            message = "Your email has been updated."
        return message

    def update_gender(self):
        if self.gender != "male" and self.gender != "female" and self.gender != "agender" and self.gender != "bigender" \
                and self.gender != "intergender" and self.gender != "other":
            message = "The gender you entered is not handled by our website."
        else:
            self.query('''UPDATE users set gender = (?) WHERE id = (?)''', (self.gender, self.user_id))
            message = "Your gender has been updated."
        return message

    def update_orientation(self):
        if self.orientation != "male" and self.orientation != "female" and self.orientation != "other" and \
                self.orientation != "both":
            message = "The orientation you entered is not handled by our website."
        else:
            self.query('''UPDATE users set orientation = (?) WHERE id = (?)''', (self.orientation, self.user_id))
            message = "Your orientation has been updated."
        return message

    def update_bio(self):
        if len(self.bio) < 10:
            message = "Your bio should at least contain 10 characters."
        else:
            self.query('''UPDATE users set bio = (?) WHERE id = (?)''', (self.bio, self.user_id))
            message = "Your bio has been updated."
        return message

    def update_birthdate(self):
        year, month, day = self.birthdate.split("-")
        now = datetime.datetime.now()
        year = int(year)
        month = int(month)
        day = int(day)
        if (year > now.year - 18 or \
                (year == now.year - 18 and month > now.month) or \
                (year == now.year - 18 and month == now.month and day > now.day)):
            return "You're too young."
        else:
            self.query('''UPDATE users set birthdate = (?) WHERE id = (?)''', (self.birthdate, self.user_id))
            return "Your date of birth has been updated."

    # This function tests if
    def auth(self, login, password):
        res = self.query('''SELECT password FROM users WHERE login=? AND confirmed == '1' ''', (login,))
        if len(res) > 0 and check_password_hash(res[0][0], password):
            res = self.query(
                '''SELECT users.id, login, gender, email, pic_id, popularity, firstname, lastname, longitude, latitude, bio, \
                orientation, birthdate, city, admin FROM users
                WHERE users.login = ? ''',
                (login,))
            dictionnary = {'id': res[0][0], 'login': res[0][1], 'gender': res[0][2], 'email': res[0][3],
                           'pic_id': res[0][4], 'popularity': res[0][5], 'firstname': res[0][6], 'lastname': res[0][7],
                           'longitude': res[0][8], 'latitude': res[0][9], 'bio': res[0][10], 'orientation': res[0][11],
                           "birthdate": res[0][12], "city": res[0][13], "admin": res[0][14]}
            self.dict_to_obj(dictionnary)
            return True
        return False

    def logout(self, user_id):
        self.query('''UPDATE users set is_connected = 0, last_connection=? WHERE id=?''',
                   (datetime.datetime.now(), user_id))
        return True

    # This request returns a list of tuples containing ((user_id, user_match_id, user_name, user_match_name),([...]))
    def matched(self, user_id):
        matches = self.query(
            '''
            SELECT u1.id AS user_id, u1.login AS user_login, l1.user_liked_id AS user_match_id, 
            u2.login AS user_match_name, p2.id AS pic_id, p2.path AS user_match_img, u2.last_connection AS like_last_connection 
            FROM likes AS l1, likes AS l2
            INNER JOIN users AS u1 ON l1.user_id=u1.id INNER JOIN users AS u2 ON l1.user_liked_id=u2.id
            INNER JOIN pics AS p1 ON u1.pic_id = p1.id INNER JOIN pics AS p2 ON u2.pic_id=p2.id
            WHERE l1.user_id = l2.user_liked_id AND l1.user_liked_id = l2.user_id AND u1.id=? ORDER BY l1.ts DESC;
            ''', (user_id,))
        return matches

    # This request returns a list of tuples containing ((user_id, user_match_id, user_name, user_match_name),([...]))
    def likes(self, user_id):
        matches = self.query(
            '''
            SELECT u2.id as user_id, u2.login AS user_login, u1.id as like_id, u1.login AS like_login, p1.id AS pic_id,
            p1.path AS like_img, u1.last_connection AS like_last_connection
            FROM likes AS l1
            INNER JOIN users AS u1 ON u1.id = l1.user_id
            INNER JOIN users AS u2 ON u2.id = l1.user_liked_id
            INNER JOIN pics AS p1 ON u1.pic_id = p1.id INNER JOIN pics AS p2 ON u2.pic_id=p2.id
            WHERE u2.id=? ORDER BY l1.ts DESC''', (user_id,))
        return matches

    # This request returns a list of tuples containing ((user_id, user_match_id, user_name, user_match_name),([...]))
    def my_likes(self, user_id):
        matches = self.query(
            '''
            SELECT u1.id AS like_id, u1.login AS like_login, u2.id as user_id, u2.login AS user_login, p2.id AS pic_id,
            p2.path AS like_img, u2.last_connection as user_last_connection
            FROM likes AS l1
            INNER JOIN users AS u1 ON u1.id = l1.user_id
            INNER JOIN users AS u2 ON u2.id = l1.user_liked_id
            INNER JOIN pics AS p1 ON u1.pic_id = p1.id INNER JOIN pics AS p2 ON u2.pic_id=p2.id
            WHERE u1.id=? ORDER BY l1.ts DESC''', (user_id,))
        return matches

    def is_matched(self, user1, user2):
        res = self.query(
            '''
            SELECT COUNT(*) AS match
            FROM likes AS l1, likes AS l2
            INNER JOIN users AS us1 ON l1.user_id=us1.id INNER JOIN users AS us2 ON l1.user_liked_id=us2.id
            INNER JOIN pics AS p1 ON us1.pic_id = p1.id INNER JOIN pics AS p2 ON us2.pic_id=p2.id
            WHERE l1.user_id = l2.user_liked_id AND l1.user_liked_id = l2.user_id AND us1.id=? AND us2.id=?;
            ''', (user1, user2))
        if len(res) > 0:
            return res[0][0] >= 1
        return False

    def does_like(self, user1_id, user2_login):
        res = self.query('''SELECT COUNT(*) FROM likes 
                                INNER JOIN users AS us2 on user_liked_id = us2.id 
                          WHERE (user_id = :user1 AND us2.login = :user2)
                          ''', {'user1': user1_id, 'user2': user2_login})
        res2 = self.query('''SELECT COUNT(*) FROM likes 
                                INNER JOIN users AS us1 ON user_id = us1.id 
                          WHERE (us1.login = :user2 AND user_liked_id = :user1)
                          ''', {'user1': user1_id, 'user2': user2_login})
        if res[0][0] > 0:
            status = 'unlike'
        elif res2[0][0] > 0:
            status = 'match'
        else:
            status = 'like'
        return status

    def get_pic(self, username):
        pic = self.query(
            '''
            SELECT pics.path FROM pics, users WHERE pics.id = users.pic_id;
            ''', (username,))
        return pic

    def to_json(self):
        res = self.query(
            '''SELECT users.id, login, gender, email, pic_id, popularity, firstname, lastname, longitude, latitude, bio, \
            orientation, birthdate, city, admin FROM users 
            WHERE users.id = ?''',
            (self.user_id,))
        return json.dumps(
            {'id': res[0][0], 'login': res[0][1], 'gender': res[0][2], 'email': res[0][3], 'pic_id': res[0][4],
             'popularity': res[0][5], 'firstname': res[0][6], 'lastname': res[0][7], 'longitude': res[0][8],
             'latitude': res[0][9], 'bio': res[0][10], 'orientation': res[0][11], "birthdate": res[0][12],
             "city": res[0][13], "admin": res[0][14]})

    def update_socket(self, user_id, socket_id):
        self.query('''UPDATE users SET socket = ? WHERE id = ?''', (socket_id, user_id))

    def get_socket(self, user_id):
        sock = self.query('''SELECT socket FROM users WHERE id = ?''', (user_id,))
        return sock

    def get_connected(self):
        res = self.query('''SELECT id FROM users WHERE is_connected = 1''', ())
        return res

    def set_connected(self, user_id, user_status):
        self.query('''UPDATE users SET is_connected=? WHERE id=?''', (user_status, user_id))
        if user_status == 0:
            self.query('''UPDATE users SET last_connection=? WHERE id=?''', (datetime.datetime.now(), user_id))
        else:
            self.query('''UPDATE users SET last_connection=0 WHERE id=?''', (user_id,))
        return True

    def password_recovery(self, email):
        new_pass = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        hashed_pass = generate_password_hash(new_pass)
        res = self.count_query('''UPDATE users SET password = ? WHERE email == ?''', (hashed_pass, email))
        self.send_email(email, 'Your password has been reset\n, Your new password is {}'.format(new_pass))
        return res

    def populate(self, data):
        location = [random.uniform(43.94068668816254, 47.53797311183746),
                    random.uniform(4.816622160114319, 4.818192239885681)]
        hashed = generate_password_hash('0000')
        user_data = (data['login']['username'], data['name']['first'], data['name']['last'],
                     data['email'], hashed, data['gender'], location[0],
                     location[1], data['dob']['date'][:data['dob']['date'].index('T')],
                     random_date(), random_text())
        self.query('''INSERT INTO users(login, firstname, lastname, email, password, gender, latitude, longitude,
          birthdate, last_connection, bio, confirmed) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '1')''',
                   user_data)
        id = self.query('''SELECT id FROM users WHERE login=?''', (data['login']['username'],))
        self.user_id = id[0][0]
        self.update_location(location[0], location[1])
        pic = Pic()
        pic_id = pic.add(data['picture']['large'], self.user_id)
        self.query('''UPDATE users SET pic_id=? WHERE login=?''', (pic_id, data['login']['username']))
        return user_data + (data['picture']['large'],)

    def search(self, data, user_id):
        sort = 'popularity DESC'
        if data['sort'] == 'age':
            sort = 'birthdate DESC'
        elif data['sort'] == "interests":
            hashy = Hashtag()
            tags = hashy.get(user_id)
            sort = "(SELECT COUNT(hashtag) FROM hashtags AS h2 WHERE h2.hashtag IN ('" + "', '".join(tags) + "')" + \
                   " AND h2.user_id = users.id) DESC"
        if len(data['hashtag']) > 0:
            res = self.query('''
            SELECT DISTINCT login, gender, birthdate, pics.path, city, latitude, longitude, orientation, popularity,
             users.id 
            FROM users 
            INNER JOIN pics ON pics.id = users.pic_id 
            LEFT JOIN blocks ON blocks.to_id = users.id AND blocks.from_id = ?
            LEFT JOIN hashtags ON users.id = hashtags.user_id 
            WHERE blocks.to_id IS NULL  
            AND users.id != ? AND login LIKE ? 
            AND birthdate < ? AND birthdate >= ?
            AND popularity >= ? AND popularity <= ?
            AND latitude >= ? AND latitude <= ?
            AND longitude >= ? AND longitude <= ? 
            AND (SELECT COUNT(hashtag) FROM hashtags WHERE hashtag IN (''' + ','.join('?' * len(data['hashtag'])) + ''') AND hashtags.user_id = users.id) >= ?
            GROUP BY users.id 
            ORDER BY ''' + sort,
                             (user_id, user_id, '%' + data['login'] + '%', data['age'][0], data['age'][1],
                              data['popularity'][0], data['popularity'][1],
                              data['distance'][0], data['distance'][1], data['distance'][2], data['distance'][3]) +
                             tuple(data['hashtag']) + (len(data['hashtag']),))
        else:
            res = self.query('''
            SELECT DISTINCT login, gender, birthdate, pics.path, city, latitude, longitude, orientation, popularity, 
            users.id 
            FROM users 
            INNER JOIN pics ON pics.id = users.pic_id 
            LEFT JOIN blocks ON blocks.to_id = users.id AND blocks.from_id = ?
            LEFT JOIN hashtags ON users.id = hashtags.user_id 
            WHERE blocks.to_id IS NULL  
            AND users.id != ? AND login LIKE ? 
            AND birthdate < ? AND birthdate >= ?
            AND popularity >= ? AND popularity <= ?
            AND latitude >= ? AND latitude <= ?
            AND longitude >= ? AND longitude <= ?
            GROUP BY users.id 
            ORDER BY ''' + sort,
                             (user_id, user_id, '%' + data['login'] + '%', data['age'][0], data['age'][1],
                              data['popularity'][0], data['popularity'][1],
                              data['distance'][0], data['distance'][1], data['distance'][2], data['distance'][3]))
        if data['sort'] == 'distance':
            res = distance_sort(data['location'], res, data['radius'])
        else:
            res = distance_filter(data['location'], res, data['radius'])
        if data['matching'] == 'true':
            self.user_id = user_id
            final = self.match_filter(res)
        else:
            final = res
        return final

    @staticmethod
    def gender_match(gender1, orientation1, gender2, orientation2):
        if orientation1 == 'both':
            orientation1 = ['male', 'female']
        else:
            orientation1 = [orientation1]
        if orientation2 == 'both':
            orientation2 = ['male', 'female']
        else:
            orientation2 = [orientation2]
        return gender1 in orientation2 and gender2 in orientation1

    def match_filter(self, res):
        info = json.loads(self.to_json())
        hash_obj = Hashtag()
        filtered = [user for user in res if User.gender_match(info['gender'], info['orientation'], user[1], user[7]) and
                    average([max(0, 100 - get_distance((info['latitude'], info['longitude']),
                                                       (user[5], user[6]))), hash_obj.common_rate(
                        user[9], info['id']),
                             100 * (max(0.1, min(info['popularity'], user[8])) / max(
                                 [0.1, info['popularity'], user[8]]))],
                            weights=[2, 3, 1]) >= 40]
        return filtered

    def update_location(self, latitude, longitude):
        response = requests.get("https://nominatim.openstreetmap.org/reverse?format=json&zoom=10&" +
                                "lat=" + str(latitude) + "&lon=" + str(longitude))
        result = response.json()
        city = result["address"]["city"]
        self.updatelocation(longitude, latitude)
        self.update_city(city)

    def is_complete(self, user_id):
        res = self.query('''SELECT COUNT(*) FROM users 
        WHERE id = ? AND 
        (bio IS NULL OR birthdate IS NULL OR pic_id IS NULL or longitude IS NULL OR latitude IS NULL)''', (user_id,))
        return res[0][0] == 0

    def get_pics(self, user_id):
        res = self.query('''SELECT * FROM pics WHERE pics.user_id = ?''', (user_id,))
        return res

    def del_pics(self, user_id, pic_id):
        res = self.query('''SELECT COUNT(*) FROM pics 
                            INNER JOIN users ON users.pic_id = pics.id 
                            WHERE users.id = ? AND pics.id = ?''', (user_id, pic_id))
        if res[0][0] == 0:
            pic = Pic()
            pic.delete(pic_id)
            return True
        return False

    def set_profile_pic(self, user_id, pic_id):
        res = self.query('''SELECT COUNT(*) FROM pics WHERE user_id = ? and id = ?''', (user_id, pic_id))
        if res[0][0] > 0:
            self.query('''UPDATE users SET pic_id = ? WHERE id = ?''', (pic_id, user_id))
            return True
        return False

    def compute_popularity(self, user_id):
        lik = Like()
        vis = Visit(user_id)
        self.query('''UPDATE users SET popularity=? WHERE id = ?''',
                   (min(100, round(average([vis.ratio(), lik.ratio(user_id)], weights=[1, 3]))),
                    user_id))
        return True

    def does_block(self, user1_id, user2_login):
        res = self.query('''SELECT COUNT(*) FROM blocks
                            INNER JOIN users ON to_id = users.id 
                            WHERE from_id = ? AND users.login = ?''', (user1_id, user2_login))
        return res[0][0] != 0

    def blocks(self, user1_id, user2_id):
        res = self.query('''SELECT COUNT(*) FROM blocks
                            INNER JOIN users ON to_id = users.id 
                            WHERE from_id = ? AND users.id = ?''', (user1_id, user2_id))
        return res[0][0] != 0

    def delete(self, user_id):
        self.query('''DELETE FROM users WHERE id = ?''', (user_id,))
        self.query('''DELETE FROM likes WHERE user_id = ? OR user_liked_id = ?''', (user_id, user_id))
        self.query('''DELETE FROM visits WHERE to_id = ? OR from_id = ?''', (user_id, user_id))
        self.query('''DELETE FROM hashtags WHERE user_id = ?''', (user_id,))
        self.query('''DELETE FROM pics WHERE user_id = ?''', (user_id,))
        self.query('''DELETE FROM blocks WHERE to_id = ? OR from_id = ?''', (user_id, user_id))
        self.query('''DELETE FROM reports WHERE to_id = ? OR from_id = ?''', (user_id, user_id))
        self.query('''DELETE FROM chat WHERE emitter_id = ? OR receiver_id = ?''', (user_id, user_id))
        self.query('''DELETE FROM notifs WHERE from_id = ? OR to_id = ?''', (user_id, user_id))

    def exists(self, username):
        res = self.query('''SELECT COUNT(*) FROM users WHERE login = ?''', (username,))
        return res[0][0] != 0


# This Class handles pics, storing and retrieving
class Pic(DBNode):

    def __init__(self):
        super(Pic, self).__init__()

    def set(self, name, user_id):
        self.query('''INSERT INTO pics(user_id, path) VALUES (?, ?)''',
                   (user_id, "/static/assets/pics/" + name))
        return True

    def add(self, url, user_id):
        self.query('''INSERT INTO pics(path, user_id) VALUES (?, ?)''', (url, user_id))
        res = self.query('''SELECT id FROM pics WHERE path = ?''', (url,))
        return res[0][0]

    def delete(self, pic_id):
        self.query('''DELETE FROM pics WHERE id = ?''', (pic_id,))
        return True


# This Class handles chat messages, storing and retrieving
class Chat(DBNode):
    emitter_id = None
    receiver_id = None
    emitter_socket = None
    receiver_socket = None

    def __init__(self, emitter_id, receiver_id):
        super(Chat, self).__init__()
        self.emitter_id = emitter_id
        self.receiver_id = receiver_id
        user = User()
        sock = user.get_socket(emitter_id)
        if len(sock) > 0:
            self.emitter_socket = sock[0]
        sock = user.get_socket(receiver_id)
        if len(sock) > 0:
            self.receiver_socket = sock[0]

    def send(self, content):
        self.query('''INSERT INTO chat(emitter_id, receiver_id, content) VALUES (?, ?, ?)''',
                   (self.emitter_id, self.receiver_id, content))
        return True

    def get(self):
        res = self.query(
            '''SELECT emitter_id, content, ts FROM chat WHERE (emitter_id = ? AND receiver_id = ?) OR (emitter_id = ? AND receiver_id = ?) ORDER BY ts ASC''',
            (self.emitter_id, self.receiver_id, self.receiver_id, self.emitter_id))
        return res

    def get_room(self):
        socks = [int(self.emitter_id), int(self.receiver_id)]
        socks.sort()
        room = str(socks[0]) + "__" + str(socks[1])
        return room


# This Class handles notifications, storing, retrieving deleting.
class Notif(DBNode):
    user_id = None

    def __init__(self, user_id):
        super(Notif, self).__init__()
        self.user_id = user_id

    def count(self):
        ct = self.query('''SELECT COUNT(*) FROM notifs WHERE to_id = ?''', (self.user_id,))
        return ct

    def get_all(self):
        notif = self.query(
            '''SELECT notifs.type, notifs.from_id, users.login, notifs.id FROM notifs 
                INNER JOIN users ON users.id = notifs.from_id 
                WHERE to_id = ? ORDER BY notifs.ts DESC''',
            (self.user_id,))
        return notif

    def send(self, to_id, notif_type):
        us = User()
        cond = us.blocks(to_id, self.user_id)
        if not cond:
            self.query('''INSERT INTO notifs(from_id, to_id, type) VALUES(?, ?, ?)''',
                       (self.user_id, to_id, notif_type))

    def flush(self, from_id, notif_type):
        self.query('''DELETE FROM notifs WHERE to_id=? AND from_id=? AND type=?''', (self.user_id, from_id, notif_type))

    def delete(self, notif_id):
        self.query('''DELETE FROM notifs WHERE to_id=? AND id=?''', (self.user_id, notif_id))


class Visit(DBNode):
    user_id = None

    def __init__(self, user_id):
        super(Visit, self).__init__()
        self.user_id = user_id

    def get_all(self):
        res = self.query(
            '''
SELECT to_id, from_id AS visit_id, users.login AS visit_login, pics.id AS pic_id, pics.path AS pic_path,
  users.last_connection AS last_connection, ts
FROM visits
INNER JOIN users on from_id = users.id
INNER JOIN pics on from_id = pics.user_id
WHERE to_id=?
ORDER BY ts DESC
''',
            (self.user_id,))
        return res

    def random(self, nb):
        id = self.query('''SELECT id FROM users ORDER BY RANDOM()''', ())
        id = [user_id[0] for user_id in id]
        values = [{'user1': random.choice(id), 'user2': random.choice(id), 'ts': random_date()} for i in range(0, nb)]
        self.multiple_query('''INSERT INTO visits(from_id, to_id, ts) SELECT :user1, :user2, :ts 
                                WHERE NOT EXISTS 
                                (SELECT 1 FROM visits WHERE from_id = :user1 AND to_id = :user2
                                  AND :user1 != :user2)''', values)

    def add_visit(self, user_profile):
        profile_id = self.query("SELECT id FROM users WHERE login = ?", (user_profile,))[0][0]
        self.query('''DELETE FROM visits WHERE from_id = ? AND to_id = ?''', (self.user_id, profile_id))
        self.query('''DELETE FROM notifs WHERE from_id = ? AND to_id = ? AND type = 'visit' ''',
                   (self.user_id, profile_id))
        self.query('''
            INSERT INTO visits (from_id, to_id) VALUES(?, ?)
        ''', (self.user_id, profile_id))
        notif = Notif(self.user_id)
        notif.send(profile_id, 'visit')
        us = User()
        us.compute_popularity(profile_id)
        us.compute_popularity(self.user_id)

    def ratio(self):
        count_to = self.query('''SELECT COUNT(*) FROM visits WHERE to_id = ?''', (self.user_id,))[0][0]
        from_to = self.query('''SELECT COUNT(*) FROM visits WHERE from_id = ?''', (self.user_id,))[0][0]
        if count_to + from_to == 0:
            return 0
        return int(100 * float(count_to) / float((count_to + from_to)))


class Like(DBNode):

    def __init__(self):
        super(Like, self).__init__()

    def random(self, nb):
        id = self.query('''SELECT id FROM users ORDER BY RANDOM()''', ())
        id = [user_id[0] for user_id in id]
        values = [{'user1': random.choice(id), 'user2': random.choice(id), 'ts': random_date()} for i in range(0, nb)]
        self.multiple_query('''INSERT INTO likes(user_id, user_liked_id, ts) SELECT :user1, :user2, :ts
                                WHERE NOT EXISTS
                                (SELECT 1 FROM likes WHERE user_id == :user1 AND user_liked_id == :user2
                                  OR :user1 == :user2)''', values)

    def switch(self, user1, user2):
        notif_obj = Notif(user1)
        us = User()
        test = self.count_query('''DELETE FROM likes WHERE user_id = ? and user_liked_id = ?''', (user1, user2))
        if test == 0:
            self.query('''INSERT INTO likes(user_id, user_liked_id) VALUES (?, ?)''', (user1, user2))
            cond = self.query('''SELECT COUNT(*) 
                                FROM likes WHERE user_id = ? AND user_liked_id = ?''', (user2, user1))[0][0]
            if cond != 0:
                notif_obj.send(user2, 'match')
            else:
                notif_obj.send(user2, 'like')
            us.compute_popularity(user1)
            us.compute_popularity(user2)
            return True
        us.compute_popularity(user1)
        us.compute_popularity(user2)
        notif_obj.send(user2, 'unlike')
        return False

    def ratio(self, user_id):
        count_to = self.query('''SELECT COUNT(*) FROM likes WHERE user_liked_id = ?''', (user_id,))[0][0]
        from_to = self.query('''SELECT COUNT(*) FROM likes WHERE user_id = ?''', (user_id,))[0][0]
        if count_to + from_to == 0:
            return 0
        return int(100 * float(count_to) / float((count_to + from_to)))


class Hashtag(DBNode):

    def __init__(self):
        super(Hashtag, self).__init__()

    def random(self, nb):
        tag_list = ['vegan', 'geek', 'bio', 'piercing', 'smoking', 'cats', 'dogs', 'christian', 'muslim', 'children',
                    'virgin', 'drugs', 'french', 'spanish', 'curvy', 'slim', 'lion', 'trans']
        res_id = self.query('''SELECT id FROM users ORDER BY RANDOM()''', ())
        id_list = [user_id[0] for user_id in res_id]
        values = [{'user_id': random.choice(id_list), 'tag': random.choice(tag_list)}
                  for i in range(0, nb)]
        self.multiple_query('''INSERT INTO hashtags(user_id, hashtag) SELECT :user_id, :tag
                                WHERE NOT EXISTS
                                  (SELECT 1 FROM hashtags WHERE user_id = :user_id AND hashtag = :tag)''', values)

    def get_distinct(self):
        tmp = self.query('''SELECT DISTINCT hashtag FROM hashtags''', ())
        res = [t[0] for t in tmp]
        return res

    def get(self, user_id):
        tmp = self.query('''SELECT hashtag FROM hashtags WHERE user_id = ?''', (user_id,))
        res = [t[0] for t in tmp]
        return res

    def common_rate(self, user1, user2):
        common = self.query('''
SELECT hashtag FROM hashtags 
WHERE user_id = ? OR user_id = ? 
GROUP BY hashtag HAVING COUNT() == 2''', (user1, user2))
        total = self.query('''SELECT COUNT(*) FROM hashtags WHERE user_id = ? OR user_id = ?''', (user1, user2))
        ratio = float(len(common)) / float(total[0][0])
        return int(200 * ratio)
