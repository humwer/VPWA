import os.path
import random
import uuid
import json
import jwt

import settings


def is_login(text: str) -> bool:
    if settings.re.fullmatch("[A-Za-z0-9]*", text):
        return True
    return False


def is_valid_mimetype(file_mimetype) -> bool:
    for mimetype in settings.app.ALLOWED_MIMETYPE:
        if file_mimetype == mimetype:
            return True
    return False


def is_valid_extension(file_extension) -> bool:
    for extension in settings.app.ALLOWED_EXTENSIONS:
        if file_extension == extension:
            return True
    return False


def validate_role(session: str, role: str) -> bool:
    conn, cursor = settings.connect_to_db()
    query = f'SELECT id FROM sessions WHERE session=?'
    result = cursor.execute(query, (session, )).fetchone()
    if result:
        query = f'SELECT role FROM users WHERE session_id=?'
        result = cursor.execute(query, (result[0], )).fetchone()
        cursor.close()
        if result[0] == role:
            return True
        return False
    cursor.close()
    return False


def validate_session(session: str) -> str:
    conn, cursor = settings.connect_to_db()
    query = f'SELECT id FROM sessions WHERE session=?'
    result = cursor.execute(query, (session, )).fetchone()
    if result:
        query = f'SELECT username FROM users WHERE session_id=?'
        result = cursor.execute(query, (result[0], )).fetchone()
        cursor.close()
        return result[0]
    cursor.close()
    return ''


def delete_session(session: str):
    conn, cursor = settings.connect_to_db()
    query = f'UPDATE sessions SET session="" WHERE session=?'
    cursor.execute(query, (session, ))
    conn.commit()
    cursor.close()


def get_posts() -> list:
    conn, cursor = settings.connect_to_db()
    query = f'SELECT * FROM posts'
    posts = cursor.execute(query).fetchall()
    cursor.close()
    data = []
    for post in posts:
        data.append({'id': post[0], 'author': post[1], 'title': post[2],
                     'tags': post[3].split(','), 'path': post[4], 'visible': post[5]})
    return sorted(data, key=lambda x: x['id'], reverse=True)


def get_post(post_id: str) -> dict:
    conn, cursor = settings.connect_to_db()
    query = f'SELECT * FROM posts WHERE id=?'
    post = cursor.execute(query, (post_id, )).fetchone()
    cursor.close()
    return post


def generate_token(user_id, login):
    refresh_token = uuid.uuid4().hex
    expired = int((settings.datetime.now() + settings.timedelta(minutes=1)).timestamp())
    return {"user_id": user_id, "username": login, "refresh_token": refresh_token, 'expired': expired}


def add_comment_to_post(post_id: str, username: str, comment: str) -> bool:
    try:
        conn, cursor = settings.connect_to_db()
        for exclude in settings.app.EXCLUDE_FOR_SSTI:
            if exclude in comment:
                comment = '<i>Возникла ошибка при формировании комментария</i>'
        query = (f'INSERT INTO comments ("post_id", "username", "comment") '
                 f'VALUES (?, ?, ?);')
        cursor.execute(query, (post_id, username, comment))
        conn.commit()
        cursor.close()
        return True
    except Exception as err:
        print(f'[-] Ошибка: {err}')
        return False


def read_file(filename: str = 'ru'):
    path_to_read = os.path.normpath(settings.app.root_path) + os.path.normpath(settings.app.UPLOAD_FOLDER)
    filename = filename.replace('../', '')
    if filename.startswith('/'):
        return ''
    path_to_file = os.path.join(path_to_read, filename)
    for exclude in settings.app.EXCLUDE_LFI:
        if exclude in filename:
            return ''
    try:
        file = open(path_to_file, 'r', encoding='utf-8')
        data = ''.join(file.readlines())
        return data
    except Exception as err:
        return ''
