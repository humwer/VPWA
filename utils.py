import os.path

from settings import *


def is_login(text: str) -> bool:
    if re.fullmatch("[A-Za-z0-9]*", text):
        return True
    return False


def is_valid_mimetype(file_mimetype) -> bool:
    for mimetype in app.ALLOWED_MIMETYPE:
        if file_mimetype == mimetype:
            return True
    return False


def is_valid_extension(file_extension) -> bool:
    for extension in app.ALLOWED_EXTENSIONS:
        if file_extension == extension:
            return True
    return False


def validate_login(login: str, password: str) -> tuple:
    if not is_login(login):
        return 0, 'Некорректный логин пользователя'
    conn, cursor = connect_to_db()
    query = f'SELECT id FROM users WHERE username="{login.lower()}" and password="{hashlib.md5(password.encode()).hexdigest()}"'
    result = cursor.execute(query).fetchone()
    if result:
        new_session = hashlib.md5(random.randbytes(10)).hexdigest()
        query = f'UPDATE sessions SET session="{new_session}" WHERE id={result[0]}'
        cursor.execute(query)
        conn.commit()
        cursor.close()
        return 1, new_session
    cursor.close()
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
    cursor.close()
    return 1, f'Новый пользователь {login} зарегистрирован!'


def validate_role(session: str, role: str) -> bool:
    conn, cursor = connect_to_db()
    query = f'SELECT id FROM sessions WHERE session="{session}"'
    result = cursor.execute(query).fetchone()
    if result:
        query = f'SELECT role FROM users WHERE session_id={result[0]}'
        result = cursor.execute(query).fetchone()
        cursor.close()
        if result[0] == role:
            return True
        return False
    cursor.close()
    return False


def validate_session(session: str) -> str:
    conn, cursor = connect_to_db()
    query = f'SELECT id FROM sessions WHERE session="{session}"'
    result = cursor.execute(query).fetchone()
    if result:
        query = f'SELECT username FROM users WHERE session_id={result[0]}'
        result = cursor.execute(query).fetchone()
        cursor.close()
        return result[0]
    cursor.close()
    return ''


def delete_session(session: str):
    conn, cursor = connect_to_db()
    query = f'UPDATE sessions SET session="" WHERE session="{session}"'
    cursor.execute(query)
    conn.commit()
    cursor.close()


def get_posts() -> list:
    conn, cursor = connect_to_db()
    query = f'SELECT * FROM posts'
    posts = cursor.execute(query).fetchall()
    cursor.close()
    data = []
    for post in posts:
        data.append({'id': post[0], 'author': post[1], 'title': post[2],
                     'tags': post[3].split(','), 'path': post[4], 'visible': post[5]})
    return sorted(data, key=lambda x: x['id'], reverse=True)


def get_post(post_id: str) -> dict:
    conn, cursor = connect_to_db()
    query = f'SELECT * FROM posts WHERE id={post_id}'
    post = cursor.execute(query).fetchone()
    cursor.close()
    return post


def get_comments_from_post(post_id: str) -> list:
    conn, cursor = connect_to_db()
    query = f'SELECT * FROM comments WHERE post_id={post_id}'
    comments = cursor.execute(query).fetchall()
    cursor.close()
    data = []
    for comment in comments:
        try:
            data.append({'username': comment[2], 'msg': render_template_string(comment[3])})
        except Exception as err:
            data.append({'username': comment[2],
                         'msg': render_template_string("<i>Возникла ошибка при формировании комментария</i>")})
    return data


def add_comment_to_post(post_id: str, username: str, comment: str) -> bool:
    try:
        conn, cursor = connect_to_db()
        for exclude in app.EXCLUDE_FOR_SSTI:
            if exclude in comment:
                comment = '<i>Возникла ошибка при формировании комментария</i>'
        query = (f'INSERT INTO comments ("post_id", "username", "comment") '
                 f'VALUES ({post_id}, "{username}", "{comment}");')
        cursor.execute(query)
        conn.commit()
        cursor.close()
        return True
    except Exception as err:
        print(f'[-] Ошибка: {err}')
        return False


def upload_file(file, info_post: dict) -> bool:
    if not is_valid_mimetype(file.mimetype):
        return False
    extension = file.filename.split('.')[-1]
    if not is_valid_extension(extension):
        return False
    conn, cursor = connect_to_db()
    try:
        query = 'SELECT COUNT(*) FROM posts'
        num_last_post = cursor.execute(query).fetchone()[0]
        new_filename = ''.join(['content_', str(num_last_post+1), '.', extension])
        path_to_upload = os.path.normpath(app.root_path) + os.path.normpath(app.UPLOAD_FOLDER)
        if extension == "svg":
            data_file = file.stream.readlines()
            for line in data_file:
                if b'a6cbab90ebc8b8fa1b3052e56d88a5e5' in line:
                    raise Exception('PATH TRAVERSAL FLAG')
            doc = etree.fromstring(b''.join([line for line in data_file]), app.PARSER)
            svg_content = etree.tostring(doc)
            file = open(os.path.join(path_to_upload, new_filename), 'wb')
            file.write(svg_content)
            file.close()
        else:
            file.save(os.path.join(path_to_upload, new_filename))
        tags = ','.join([tag.strip() for tag in info_post['tags'].split(',')])
        path_in_db = app.UPLOAD_FOLDER + new_filename
        query = (f'INSERT INTO "posts" ("username", "title", "tags", "content_path", "visible") '
                 f'VALUES ("{info_post['username']}", "{info_post['title']}", "{tags}", "{path_in_db}", 1);')
        cursor.execute(query)
        conn.commit()
    except Exception as err:
        print(f'[-] {err}')
        cursor.close()
        return False
    return True


def read_file(filename: str = 'ru'):
    path_to_read = os.path.normpath(app.root_path) + os.path.normpath(app.UPLOAD_FOLDER)
    filename = filename.replace('../', '')
    path_to_file = os.path.join(path_to_read, filename)
    for exclude in app.EXCLUDE_LFI:
        if exclude in filename:
            return ''
    try:
        file = open(path_to_file, 'r', encoding='utf-8')
        data = ''.join(file.readlines())
        return data
    except Exception as err:
        return ''



def search_posts(column, value) -> list:
    data = []

    try:
        conn, cursor = connect_to_db()
        if "'" in value or ";" in value:
            raise Exception("[?] Крутят скулю в поиске")
        if ";" in column:
            raise Exception("[?] Крутят скулю в фильтре и пытаются сделать stacked")
        query = f"SELECT * FROM posts WHERE {column} like '%{value}%';"
        posts = cursor.execute(query).fetchall()
        cursor.close()
        for post in posts:
            data.append({'id': post[0], 'author': post[1], 'title': post[2],
                         'tags': post[3].split(','), 'path': post[4], 'visible': post[5]})
        return sorted(data, key=lambda x: x['id'], reverse=True)

    except Exception as err:
        print(f"[?] {err}")
        return data
