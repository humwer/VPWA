from flask import (Flask, render_template_string, render_template, request, make_response, send_from_directory,
                   redirect)
from datetime import datetime
from lxml import etree
import sqlite3
import hashlib
import random
import os
import re

# ---------------->
app = Flask(__name__)
app.db_name = 'sqli.db'
host = "0.0.0.0"
port = 6177
# ----------------<
app.flag_auth = "FLAG{Us3r_1npu7_v4l1d4t10n_1s_1mp0r74n7!}"
app.flag_sqli = "FLAG{D0_u_l1k3_SQL_1nj3ct10ns?}"
app.flag_xss = ""
app.flag_ssti = ""
app.flag_xxe = ""
app.flag_path = ""
# ---------------->


def connect_to_db() -> tuple:
    conn = sqlite3.connect(app.db_name)
    cursor = conn.cursor()
    return conn, cursor


def multiple_queries_to_db(query, cursor, conn):
    st = ''

    for i in query:
        cursor.execute(i)
        conn.commit()

        st = st + ''.join(cursor.fetchall())
    return st


def prepare_db():
    if os.path.exists(app.db_name):
        os.remove(app.db_name)

    conn, cursor = connect_to_db()

    adm_pass = hashlib.md5("$up3rm3g4d1ff1cul7p@$$w0rd".encode()).hexdigest()
    sup_pass = hashlib.md5("123456".encode()).hexdigest()

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
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") VALUES (1,"admin","{adm_pass}", "admin", "1");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") VALUES (2,"support","{sup_pass}", "support", "2");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") VALUES (3,"Franky","{adm_pass}", "user", "3");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") VALUES (4,"Alice","{adm_pass}", "user", "4");',
               f'INSERT INTO "users" ("id","username","password", "role", "session_id") VALUES (5,"C00lB0y","{adm_pass}", "user", "5");',
               f'INSERT INTO "flag" ("id", "flag_value") VALUES (1337,"{app.flag_sqli}");'
               ]

    data = multiple_queries_to_db(queries, cursor, conn)
    cursor.close()
    print('[+] Database sqli.db was created!')


def prepare():
    prepare_db()
