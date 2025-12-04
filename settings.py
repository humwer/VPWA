from flask import (Flask, render_template_string, render_template, request, make_response, send_from_directory,
                   redirect, url_for)
from werkzeug.exceptions import HTTPException
from datetime import datetime, timedelta
from lxml import etree
from constants import *
import modules.loader as modules
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
app.DB_NAME = 'sql.db'
app.UPLOAD_FOLDER = '/static/'
app.ALLOWED_EXTENSIONS = ('gif', 'jpg', 'jpeg', 'png', 'svg')
app.ALLOWED_MIMETYPE = ('image/gif', 'image/jpeg', 'image/png', 'image/svg+xml')
app.EXCLUDE_LFI = [':', '.py', '.ini', XXE_FILE]
app.EXCLUDE_FOR_SSTI = ('popen', 'write', 'os', 'import', 'mro', 'exec')
# ----------------<
app.config['flag'] = FLAG_SSTI
app.secret_key = "$ur3, d0 u 7h1nk 7h1s 1s 7h3 wh013 $3cr3t?"

# ---------------->
app.PARSER = etree.XMLParser(resolve_entities=True, load_dtd=True, no_network=False)


# Загрузка модулей
# ----------------
profile = modules.read_profile()
validate_registration = modules.load_validation_registration_module(profile['validate_registration'])
validate_login = modules.load_validate_login_module(profile['validate_login'])
search_posts = modules.load_search_posts_module(profile['search_posts'])
refresh_token = modules.load_refresh_token_module(profile['refresh_token'])
get_comments_from_post = modules.load_get_comments_from_post_module(profile['get_comments_from_post'])
upload_file = modules.load_upload_file_module(profile['upload_file'])
# ----------------


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
        );""", f"""
        CREATE TABLE IF NOT EXISTS "flag_{RAND_FLAG_TABLE}" (
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
               f'INSERT INTO "sessions" ("id") VALUES ({ADMIN_ID}), ({SUPPORT_ID}), ({UNIQ_ID[2]}), ({UNIQ_ID[3]}), ({UNIQ_ID[4]});',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES ({ADMIN_ID},"admin","{ADMIN_PASS}", "admin", "{ADMIN_ID}");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES ({SUPPORT_ID},"support","{SUPPORT_PASS}", "support", "{SUPPORT_ID}");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES ({UNIQ_ID[2]},"Franky","{hashlib.md5(random.randbytes(3)).hexdigest()}", "user", "{UNIQ_ID[2]}");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES ({UNIQ_ID[3]},"Alice","{hashlib.md5(random.randbytes(4)).hexdigest()}", "user", "{UNIQ_ID[3]}");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") '
               f'VALUES ({UNIQ_ID[4]},"C00lB0y","{hashlib.md5(random.randbytes(5)).hexdigest()}", "user", "{UNIQ_ID[4]}");',
               f'INSERT INTO "flag_{RAND_FLAG_TABLE}" ("id", "flag_value") VALUES (1337,"{FLAG_SQLI}");', """
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
               f'INSERT INTO "posts" ("id", "username", "title", "tags", "content_path", "visible") '
               f'VALUES (5, "C00lB0y", "Решил CTF от Пенитрагона", "Image,CTF,Penitragon", "/static/content_5.png", 1);',
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
        f'VALUES (5, 2, "support", "Ты про этот /tmp/{XXE_FILE}? Ага...<br>Слушай, а ты обезопасил форму загрузки постов? >_> ");',
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
    path_to_file = f'/tmp/{PT_FILE}'
    file = open(path_to_file, 'w')
    file.write(FLAG_PT)
    file.close()
    path_to_file = f'/tmp/{XXE_FILE}'
    file = open(path_to_file, 'w')
    file.write(FLAG_XXE)
    file.close()


def prepare():
    prepare_db()
    prepare_comments_db()
    # prepare_files_with_flags()
