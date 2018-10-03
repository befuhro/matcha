import sqlite3


def init_db():
    con = sqlite3.connect('/data/matcha.sqlite')
    cur = con.cursor()
    with open('matcha/schema.sql', 'r') as f:
        cur.executescript(f.read())