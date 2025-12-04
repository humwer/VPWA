from utils import *

'''
Boolean-based SQLi в форме логина (без возможности напрямую войти под пользователем support)
'''


def validate_login(login: str, password: str) -> tuple:
    conn, cursor = settings.connect_to_db()
    login = login.replace(';', '')
    query = f"SELECT id FROM users WHERE password=? and username='{login}'"
    try:
        result = cursor.execute(query, (settings.hashlib.md5(password.encode()).hexdigest(), )).fetchone()
    except Exception as err:
        return 0, None, 'Что-то пошло не так...'
    if result:
        if result[0] == settings.SUPPORT_ID:
            return 0, None, 'Support так просто не сдаётся!'
        payload = generate_token(result[0], login)
        new_session = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        query = f'UPDATE sessions SET session=?, refresh_token=? WHERE id=?'
        cursor.execute(query, (new_session, payload['refresh_token'], result[0]))
        conn.commit()
        cursor.close()
        return 1, new_session, 'Успешный вход'
    cursor.close()
    return 0, None, 'Неверный логин/пароль'
