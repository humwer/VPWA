from settings import *


def is_login(text: str) -> bool:
    if re.fullmatch("[A-Za-z0-9]*", text):
        return True
    return False


def validate_login(login: str, password: str) -> tuple:
    if not is_login(login):
        return 0, 'Некорректный логин пользователя'
    conn, cursor = connect_to_db()
    query = f'SELECT id FROM users WHERE username="{login}" and password="{hashlib.md5(password.encode()).hexdigest()}"'
    result = cursor.execute(query).fetchone()
    if result:
        new_session = hashlib.md5(random.randbytes(10)).hexdigest()
        query = f'UPDATE sessions SET session="{new_session}" WHERE id={result[0]}'
        cursor.execute(query)
        conn.commit()
        return 1, new_session
    return 0, ''


def validate_registration(login: str, password: str, confirm_password: str) -> tuple:
    if not is_login(login):
        return 0, 'Некорректный логин пользователя!'
    if password != confirm_password:
        return 0, 'Пароли не совпадают!'
    conn, cursor = connect_to_db()
    query = f'SELECT username FROM users WHERE username like "{login}"'
    result = cursor.execute(query).fetchone()
    if result:
        if login != result[0]:
            if login.lower() == 'support':
                return 0, 'Пользователю support запрещена смена пароля!'
            query = f'UPDATE users SET password="{hashlib.md5(password.encode()).hexdigest()}" WHERE username="{result[0]}"'
            cursor.execute(query)
            conn.commit()
            return 1, f'Новый пользователь {login} зарегистрирован!'
        return 0, 'Такой пользователь уже зарегистрирован!'
    query = f'INSERT INTO "users" ("username","password", "role") VALUES ("{login}","{hashlib.md5(password.encode()).hexdigest()}", "user");'
    cursor.execute(query)
    conn.commit()
    query = f'SELECT id FROM users WHERE username="{login}"'
    result = cursor.execute(query).fetchone()
    conn.commit()
    queries = [f'INSERT INTO sessions ("id") VALUES ({result[0]})',
               f'UPDATE users SET session_id={result[0]} WHERE username="{login}"']
    multiple_queries_to_db(queries, cursor, conn)
    return 1, f'Новый пользователь {login} зарегистрирован!'


def validate_session(session: str) -> str:
    conn, cursor = connect_to_db()
    query = f'SELECT id FROM sessions WHERE session="{session}"'
    result = cursor.execute(query).fetchone()
    if result:
        query = f'SELECT username FROM users WHERE session_id={result[0]}'
        result = cursor.execute(query).fetchone()
        return result[0]
    return ''


def delete_session(session: str):
    conn, cursor = connect_to_db()
    query = f'UPDATE sessions SET session="" WHERE session="{session}"'
    cursor.execute(query)
    conn.commit()


def get_posts() -> list:
    conn, cursor = connect_to_db()
    query = f'SELECT * FROM posts'
    posts = cursor.execute(query).fetchall()
    data = []
    for post in posts:
        data.append({'id': post[0], 'author': post[1], 'title': post[2],
                     'tags': post[3].split(','), 'path': post[4], 'visible': post[5]})
    return data


def get_post(post_id: str) -> dict:
    conn, cursor = connect_to_db()
    query = f'SELECT * FROM posts WHERE id={post_id}'
    post = cursor.execute(query).fetchone()
    return post


def get_comments_from_post(post_id: str) -> list:
    conn, cursor = connect_to_db()
    query = f'SELECT * FROM comments WHERE post_id={post_id}'
    comments = cursor.execute(query).fetchall()
    data = []
    for comment in comments:
        data.append({'username': comment[2], 'msg': comment[3]})
    return data
