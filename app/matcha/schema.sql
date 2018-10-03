DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS hashtags;
DROP TABLE IF EXISTS pics;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS chat;
DROP TABLE IF EXISTS notifs;
DROP TABLE IF EXISTS visits;
DROP TABLE IF EXISTS blocks;
DROP TABLE IF EXISTS reports;

CREATE TABLE IF NOT EXISTS users
(
  id              INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  login           TEXT,
  firstname       TEXT,
  lastname        TEXT,
  gender          TEXT,
  email           TEXT,
  password        TEXT,
  orientation     TEXT                DEFAULT 'both',
  bio             TEXT,
  birthdate       TINYTEXT,
  pic_id          INTEGER,
  popularity      INTEGER             DEFAULT 0,
  longitude       TINYTEXT,
  latitude        TINYTEXT,
  last_connection TIMESTAMP           DEFAULT 0,
  is_connected    INTEGER,
  city            TEXT,
  socket          TEXT,
  admin           INT,
  confirmed       INT                 DEFAULT 0
);

INSERT INTO users (login, firstname, lastname, gender, email, password, admin, confirmed)
VALUES ('admin', 'Oreo', 'Befuhro', 'other', 'admin@example.com',
        'pbkdf2:sha256:50000$1wEMaVK6$e3a9e9a1c6f0ee4d0afc5deb4d262d63e8e535453b01e9df07d831ab60609592', 1, 1);

CREATE TABLE if NOT EXISTS hashtags
(
  id      INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  user_id INTEGER,
  hashtag TEXT
);

CREATE TABLE IF NOT EXISTS pics
(
  id      INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  user_id INTEGER,
  path    TEXT
);

CREATE TABLE IF NOT EXISTS likes
(
  id            INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  user_id       INTEGER,
  user_liked_id INTEGER,
  ts            TIMESTAMP           DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat
(
  id          INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  emitter_id  INTEGER,
  receiver_id INTEGER,
  content     TEXT,
  ts          TIMESTAMP           DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifs
(
  id      INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  from_id INTEGER,
  to_id   INTEGER,
  type    TEXT,
  ts      TIMESTAMP           DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS visits
(
  id      INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  from_id INTEGER,
  to_id   INTEGER,
  ts      TIMESTAMP           DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blocks
(
  id      INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  from_id INTEGER,
  to_id   INTEGER
);

CREATE TABLE IF NOT EXISTS reports
(
  id      INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  from_id INTEGER,
  to_id   INTEGER,
  ts      TIMESTAMP           DEFAULT CURRENT_TIMESTAMP
);