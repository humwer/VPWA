from settings import *


def is_login(text: str) -> bool:
    if re.fullmatch("[A-Za-z0-9]*", text):
        return True
    return False


def validate_login(login, password) -> tuple:
    conn, cursor = connect_to_db()
    if not is_login(login):
        return 0, 'Bad login'
    query = f'SELECT id FROM users WHERE username="{login}" and password="{hashlib.md5(password.encode()).hexdigest()}"'
    result = cursor.execute(query).fetchone()
    if result:
        new_session = hashlib.md5(random.randbytes(10)).hexdigest()
        query = f'UPDATE sessions SET session="{new_session}" WHERE id={result[0]}'
        cursor.execute(query)
        conn.commit()
        return 1, new_session
    return 0, ''


def validate_session(session) -> str:
    conn, cursor = connect_to_db()
    query = f'SELECT id FROM sessions WHERE session="{session}"'
    result = cursor.execute(query).fetchone()
    if result:
        query = f'SELECT username FROM users WHERE session_id={result[0]}'
        result = cursor.execute(query).fetchone()
        return result[0]
    return ''


def delete_session(session):
    conn, cursor = connect_to_db()
    query = f'UPDATE sessions SET session="" WHERE session="{session}"'
    cursor.execute(query)
    conn.commit()
