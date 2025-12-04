from utils import *

'''
Безопасная форма входа
'''


def validate_login(login: str, password: str) -> tuple:
    if not is_login(login):
        return 0, 'Некорректный логин пользователя'
    conn, cursor = settings.connect_to_db()
    query = f'SELECT id FROM users WHERE password=? and username=?'
    result = cursor.execute(query, (login.lower(), settings.hashlib.md5(password.encode()).hexdigest(), )).fetchone()
    if result:
        payload = generate_token(result[0], login)
        new_session = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        query = f'UPDATE sessions SET session=?, refresh_token=? WHERE id=?'
        cursor.execute(query, (new_session, payload['refresh_token'], result[0]))
        conn.commit()
        cursor.close()
        return 1, new_session, 'Успешный вход'
    cursor.close()
    return 0, None, 'Неверный логин/пароль'
