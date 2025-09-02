from flask import (Flask, render_template_string, render_template, request, make_response, send_from_directory,
                   redirect, url_for)
from werkzeug.exceptions import HTTPException
from datetime import datetime, timedelta
from lxml import etree
import requests
import sqlite3
import hashlib
import base64
import random
import time
import os
import re

# ---------------->
app = Flask(__name__)
app.DB_NAME = 'sqli.db'
app.UPLOAD_FOLDER = '/static/'
app.ALLOWED_EXTENSIONS = ('gif', 'jpg', 'jpeg', 'png', 'svg')
app.ALLOWED_MIMETYPE = ('image/gif', 'image/jpeg', 'image/png', 'image/svg+xml')
app.EXCLUDE_LFI = [':', '.py', '.ini', '1bf549a3128aaf9f20293d2566651703']
app.EXCLUDE_FOR_SSTI = ('popen', 'write', 'os', 'import', 'mro', 'exec')
host = "0.0.0.0"
port = 6177
SECRET_KEY = 'w0wth1s1$Sup3R$3CR37K3y!!!'
# ----------------<
app.flag_auth = "FLAG{N3w_func710n_4_r3g1$7r4710n!}"        # +
app.flag_brute = "FLAG{W34k_p@$$w0rd_1$_7r0bl3!}"           # +
app.flag_sqli = "FLAG{D0_u_l1k3_$QL_1nj3c710n$?}"           # +
app.flag_xss = "FLAG{0op$_c00k13_w17h0u7_h77p_0n1y?}"       # +
app.flag_ssti = "FLAG{My_f4v0ur173_73mp1473$_1nj3c710n}"    # +
app.flag_xxe = "FLAG{1_7h0ugh7_w0u1d_b3_7h3_p1c7ur3}"       # +
app.flag_path = "FLAG{W4F_1$n7_7h3_pr0bl3m_70_u?}"          # +
app.flag_ssrf = "FLAG{1n73rn4l_$3rv3r_1$n7_1n73rn4l?}"      # +
app.config['flag'] = app.flag_ssti
app.secret_key = "$ur3, d0 u 7h1nk 7h1s 1s 7h3 wh013 $3cr3t?"

# ---------------->
app.PARSER = etree.XMLParser(resolve_entities=True)


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
                "id"            INTEGER NOT NULL UNIQUE DEFAULT (abs(random()) % 900000 + 100000),
                "username"      TEXT(3, 50) NOT NULL UNIQUE,
                "password"      TEXT(3, 50) NOT NULL,
                "role"          TEXT(3, 50) NOT NULL,
                "session_id"    INTEGER,
                FOREIGN KEY(session_id) REFERENCES sessions(id),
                PRIMARY KEY("id")
        );""", """
        CREATE TABLE IF NOT EXISTS "flag" (
                "id"            INTEGER NOT NULL UNIQUE,
                "flag_value"    TEXT(50)
        );""", """
        CREATE TABLE IF NOT EXISTS "comments" (
                "id"            INTEGER NOT NULL UNIQUE,
                "post_id"       INTEGER NOT NULL,
                "username"      TEXT(3, 50) NOT NULL,
                "comment"       TEXT(200) NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
        );""", """
        CREATE TABLE IF NOT EXISTS "sessions" (
                "id"                    INTEGER NOT NULL UNIQUE,
                "session"               TEXT(32),
                "refresh_token"         TEXT(32)
        );""",
               f'INSERT INTO "sessions" ("id") VALUES (643792), (236045), (945635), (234845), (112359);',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES (643792,"admin","{hashlib.md5("$up3rm3g4d1ff1cul7p@$$w0rd@#__?.<#".encode()).hexdigest()}", "admin", "643792");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES (236045,"support","{hashlib.md5("trustno1".encode()).hexdigest()}", "support", "236045");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES (945635,"Franky","{hashlib.md5(random.randbytes(3)).hexdigest()}", "user", "945635");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES (234845,"Alice","{hashlib.md5(random.randbytes(4)).hexdigest()}", "user", "234845");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES (112359,"C00lB0y","{hashlib.md5(random.randbytes(5)).hexdigest()}", "user", "112359");',
               f'INSERT INTO "flag" ("id", "flag_value") VALUES (1337,"{app.flag_sqli}");', """
       CREATE TABLE IF NOT EXISTS "posts" (
               "id"            INTEGER NOT NULL UNIQUE,
               "username"      TEXT(3, 50) NOT NULL,
               "title"         TEXT NOT NULL,
               "tags"          TEXT(200) NOT NULL,
               "content_path"  TEXT NOT NULL,
               "visible"       INTEGER DEFAULT 1 NOT NULL,
               PRIMARY KEY("id" AUTOINCREMENT)
       );""",
               f'INSERT INTO "posts" ("id", "username", "title", "tags", "content_path", "visible") '
               f'VALUES (1, "admin", "Добро пожаловать на наш портал!", "Image,Welcome", "/static/content_1.png", 1);',
               f'INSERT INTO "posts" ("id", "username", "title", "tags", "content_path", "visible") '
               f'VALUES (2, "admin", "Технические работы!", "Test", "/static/content_2.jpg", 0);',
               f'INSERT INTO "posts" ("id", "username", "title", "tags", "content_path", "visible") '
               f'VALUES (3, "Alice", "Милый котик :)", "Cats,Image,Cute", "/static/content_3.jpg", 1);',
               f'INSERT INTO "posts" ("id", "username", "title", "tags", "content_path", "visible") '
               f'VALUES (4, "C00lB0y", "Хацкеры такие хацкеры", "Image,Humor", "/static/content_4.jpg", 1);',
               ]

    data = multiple_queries_to_db(queries, cursor, conn)
    cursor.close()
    print('[+] Database sqli.db was created!')


def prepare_comments_db():
    conn, cursor = connect_to_db()
    queries = [
        f'INSERT INTO "comments" ("id", "post_id", "username", "comment") '
        f'VALUES (1, 1, "admin", "Всем привет! Добавил комментарии к постам, буду рад, если проверите их работу :)");',
        f'INSERT INTO "comments" ("id", "post_id", "username", "comment") '
        f'VALUES (2, 1, "C00lB0y", "Круто, прикрутили комментарии!");',
        f'INSERT INTO "comments" ("id", "post_id", "username", "comment") '
        f'VALUES (3, 1, "Franky", "<b>С00lB0y</b>, давай без спама ток");',

        f'INSERT INTO "comments" ("id", "post_id", "username", "comment") '
        f'VALUES (4, 2, "admin", "<b>support</b>, ты посмотрел тот файлик? ^.^");',
        f'INSERT INTO "comments" ("id", "post_id", "username", "comment") '
        f'VALUES (5, 2, "support", "Ты про этот /tmp/1bf549a3128aaf9f20293d2566651703? Ага...<br>Слушай, а ты обезопасил форму загрузки постов? >_> ");',
        f'INSERT INTO "comments" ("id", "post_id", "username", "comment") '
        f'VALUES (6, 2, "admin", "А? Да не, всё должно быть пучком, не переживай :) :)");',
        f'INSERT INTO "comments" ("id", "post_id", "username", "comment") '
        f'VALUES (7, 2, "support", "Ага, верю. Кстати, а ничего что мы здесь детали обсуждаем? ._.");',
        f'INSERT INTO "comments" ("id", "post_id", "username", "comment") '
        f'VALUES (8, 2, "admin", "Не парься, я просто скрою этот пост и всё будет ок :)");',
    ]
    data = multiple_queries_to_db(queries, cursor, conn)
    cursor.close()
    print('[+] Comments to database sqli.db were add!')


def prepare_files_with_flags():
    path_to_file = '/tmp/a6cbab90ebc8b8fa1b3052e56d88a5e5'
    file = open(path_to_file, 'w')
    file.write(app.flag_path)
    file.close()
    path_to_file = '/tmp/1bf549a3128aaf9f20293d2566651703'
    file = open(path_to_file, 'w')
    file.write(app.flag_xxe)
    file.close()


def prepare():
    prepare_db()
    prepare_comments_db()
    #prepare_files_with_flags()
