import datetime
import requests
import random
from math import sin, cos, sqrt, atan2, radians, trunc


def random_date():
    year = random.randint(2016, 2018)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return "%02d-%02d-%02d %02d:%02d:00" % (year, month, day, hour, minute)


def format_timestamp(messages, current_id):
    now = datetime.datetime.utcnow()
    for i in range(len(messages)):
        delta = int((now - datetime.datetime.strptime(messages[i][2], '%Y-%m-%d %H:%M:%S')).total_seconds())
        if delta // 31622400 > 0:
            years = (delta // 31622400)
            messages[i] = (int(messages[i][0] == current_id), messages[i][1],
                           "%d years ago" % (delta // 31622400) if years > 1 else "A year ago")
        elif delta // 2592000 > 0:
            months = (delta / 2592000)
            messages[i] = (int(messages[i][0] == current_id), messages[i][1],
                           "%d months ago" % (delta // 2592000) if months > 1 else "A month ago")
        elif delta // 604800 > 0:
            weeks = (delta // 604800)
            messages[i] = (int(messages[i][0] == current_id), messages[i][1],
                           "%d weeks ago" % (delta // 604800) if weeks > 1 else "A week ago")
        elif delta // 86400 > 0:
            days = (delta // 86400)
            messages[i] = (int(messages[i][0] == current_id), messages[i][1],
                           "%d days ago" % (delta // 86400) if days > 1 else "A day ago")
        elif delta // 3600 > 0:
            hours = (delta // 3600)
            messages[i] = (int(messages[i][0] == current_id), messages[i][1],
                           "%d hours ago" % (delta // 3600) if hours > 1 else "An hour ago")
        elif delta // 60 > 0:
            minutes = (delta // 60)
            messages[i] = (int(messages[i][0] == current_id), messages[i][1],
                           "%d minutes ago" % (delta // 60) if minutes > 1 else "A minute ago")
        else:
            messages[i] = (int(messages[i][0] == current_id), messages[i][1],
                           "%d seconds ago" % delta if delta > 1 else "A second ago")
    return messages


def time_delta(ts):
    now = datetime.datetime.utcnow()
    if '.' in ts:
        delta = int((now - datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f')).total_seconds())
    else:
        delta = int((now - datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')).total_seconds())
    if delta // 31622400 > 0:
        years = (delta // 31622400)
        return "%d years ago" % (delta // 31622400) if years > 1 else "a year ago"
    elif delta // 2592000 > 0:
        months = (delta // 2592000)
        return "%d months ago" % (delta // 2592000) if months > 1 else "a month ago"
    elif delta // 604800 > 0:
        weeks = (delta // 604800)
        return "%d weeks ago" % (delta // 604800) if weeks > 1 else "a week ago"
    elif delta // 86400 > 0:
        days = (delta // 86400)
        return "%d days ago" % (delta // 86400) if days > 1 else "a day ago"
    elif delta // 3600 > 0:
        hours = (delta // 3600)
        return "%d hours ago" % (delta // 3600) if hours > 1 else "an hour ago"
    elif delta // 60 > 0:
        minutes = (delta // 60)
        return "%d minutes ago" % (delta // 60) if minutes > 1 else "a minute ago"
    else:
        return "%d seconds ago" % delta if delta > 1 else "a second ago"


def age_to_date(age_min, age_max):
    now = datetime.datetime.utcnow()
    back_then = [datetime.date(now.year - int(age_min), now.month, now.day).strftime('%Y-%m-%d'),
                 datetime.date(now.year - int(age_max) - 1, now.month, now.day + 1).strftime('%Y-%m-%d')]
    return back_then


def date_to_age(birthdate):
    if birthdate is None:
        return 0
    birth = datetime.datetime.strptime(birthdate, '%Y-%m-%d')
    now = datetime.datetime.utcnow()
    age = (now - birth).days / 365
    return trunc(age)


def populate(num):
    r = requests.get('https://randomuser.me/api/?results=' + str(num))
    return r


def random_text():
    words_file = open('matcha/static/assets/words.txt', 'r')
    word_list = [line.strip('\n') for line in words_file.readlines()]
    sentence = ""
    for i in range(0, 30):
        sentence += random.choice(word_list) + ' '
    return sentence


def distance_sort(origin, res, radius):
    r = distance_filter(origin, res, radius)
    sort_res = sorted(r, key=lambda x: x[-1])
    return sort_res


def distance_filter(origin, res, radius):
    r = []
    n = 0
    for i in range(0, len(res)):
        dist = get_distance(origin, (res[i][5], res[i][6]))
        if dist <= radius:
            r.append(list(res[i]))
            r[n].append(dist)
            n += 1
    return r


def get_distance(pt1, pt2):
    pt1 = (radians(abs(float(pt1[0]))), radians(abs(float(pt1[1]))))
    pt2 = (radians(abs(float(pt2[0]))), radians(abs(float(pt2[1]))))
    dpt = (pt1[0] - pt2[0], pt1[1] - pt2[1])
    a = sin(dpt[0] / 2) ** 2 + cos(pt1[0]) * cos(pt2[0]) * sin(dpt[1] / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6373.0 * c
    return round(distance)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg']
