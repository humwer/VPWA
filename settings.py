from flask import (Flask, render_template_string, render_template, request, make_response, send_from_directory,
                   redirect)
from datetime import datetime
from lxml import etree
import sqlite3
import hashlib
import base64
import random
import os
import re

# ---------------->
app = Flask(__name__)
app.DB_NAME = 'sqli.db'
app.UPLOAD_FOLDER = '/static/'
app.ALLOWED_EXTENSIONS = set(['svg', 'png', 'jpg', 'jpeg', 'gif'])
host = "0.0.0.0"
port = 6177
# ----------------<
app.flag_auth = "FLAG{Us3r_1npu7_v4l1d4t10n_1s_1mp0r74n7!}"
app.flag_sqli = "FLAG{D0_u_l1k3_SQL_1nj3ct10ns?}"
app.flag_xss = "FLAG{0ops_c00k13_w17h0u7_h77p_0n1y?}"
app.flag_ssti = "FLAG{My_f4v0ur173_73mp1473s_1nj3c710n}"
app.flag_xxe = "FLAG{1_7h0ugh7_w0u1d_b3_7h3_p1c7ur3}"
app.flag_path = "FLAG{W4F_1sn7_7h3_pr0bl3m_t0_u?}"


# ---------------->


def connect_to_db() -> tuple:
    conn = sqlite3.connect(app.DB_NAME)
    cursor = conn.cursor()
    return conn, cursor


def convert_to_base64_data(filename):
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return base64.b64encode(bytes(bytearray(blob_data))).decode('utf-8')


def multiple_queries_to_db(query, cursor, conn):
    st = ''

    for i in query:
        cursor.execute(i)
        conn.commit()

        st = st + ''.join(cursor.fetchall())
    return st


def prepare_db():
    if os.path.exists(app.DB_NAME):
        os.remove(app.DB_NAME)

    conn, cursor = connect_to_db()

    queries = ['PRAGMA case_sensitive_like=ON;', """
        CREATE TABLE IF NOT EXISTS "users" (
                "id"    INTEGER NOT NULL UNIQUE,
                "username"      TEXT(3, 50) NOT NULL UNIQUE,
                "password"      TEXT(3, 50) NOT NULL,
                "role"          TEXT(3, 50) NOT NULL,
                "session_id"              INTEGER,
                FOREIGN KEY(session_id) REFERENCES sessions(id),
                PRIMARY KEY("id" AUTOINCREMENT)
        );""", """
        CREATE TABLE IF NOT EXISTS "flag" (
                "id"    INTEGER NOT NULL UNIQUE,
                "flag_value"    TEXT(50)
        );""", """
        CREATE TABLE IF NOT EXISTS "sessions" (
                "id"    INTEGER NOT NULL UNIQUE,
                "session"    TEXT(32)
        );""",
               f'INSERT INTO "sessions" ("id") VALUES (1), (2), (3), (4), (5);',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES (1,"admin","{hashlib.md5("$up3rm3g4d1ff1cul7p@$$w0rd@#__?.<#".encode()).hexdigest()}", "admin", "1");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES (2,"support","{hashlib.md5("trustno1".encode()).hexdigest()}", "support", "2");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES (3,"Franky","{hashlib.md5(random.randbytes(3)).hexdigest()}", "user", "3");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES (4,"Alice","{hashlib.md5(random.randbytes(4)).hexdigest()}", "user", "4");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES (5,"C00lB0y","{hashlib.md5(random.randbytes(5)).hexdigest()}", "user", "5");',
               f'INSERT INTO "flag" ("id", "flag_value") VALUES (1337,"{app.flag_sqli}");', """
       CREATE TABLE IF NOT EXISTS "posts" (
               "id"            INTEGER NOT NULL UNIQUE,
               "username"      TEXT(3, 50) NOT NULL,
               "title"         TEXT NOT NULL,
               "tags"    TEXT(200) NOT NULL,
               "content_path"  TEXT NOT NULL,
               "visible"       INTEGER NOT NULL,
               PRIMARY KEY("id" AUTOINCREMENT)
       );""",
               f'INSERT INTO "posts" ("id", "username", "title", "tags", "content_path", "visible") '
               f'VALUES (1, "admin", "Добро пожаловать на нашу площадку!", "Image,Welcome", "/static/content_1.png", 1);',
               f'INSERT INTO "posts" ("id", "username", "title", "tags", "content_path", "visible") '
               f'VALUES (2, "admin", "Технические работы!", "Test", "/static/content_2.jpg", 1);',
               ]

    data = multiple_queries_to_db(queries, cursor, conn)
    cursor.close()
    print('[+] Database sqli.db was created!')


def prepare():
    prepare_db()
