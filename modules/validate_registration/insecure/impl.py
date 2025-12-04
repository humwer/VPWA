from utils import *

'''
Имеется возможность перерегистрации (смена пароля) пользователя при обходе проверки (регистр) имени пользователя
'''


def validate_registration(login: str, password: str, confirm_password: str) -> tuple:
    if not is_login(login):
        return 0, 'Некорректный логин пользователя!'
    if password != confirm_password:
        return 0, 'Пароли не совпадают!'
    conn, cursor = settings.connect_to_db()
    query = f'SELECT username FROM users WHERE username like ?'
    result = cursor.execute(query, (login, )).fetchone()
    if result:
        if login != result[0]:
            if login.lower() == 'support':
                return 0, 'Пользователю support запрещена смена пароля!'
            query = f'UPDATE users SET password=? WHERE username=?'
            cursor.execute(query, (settings.hashlib.md5(password.encode()).hexdigest(), result[0], ))
            conn.commit()
            return 1, f'Новый пользователь {login} зарегистрирован!'
        return 0, 'Такой пользователь уже зарегистрирован!'
    random_id = random.randint(100000, 999999)
    while cursor.execute(f'SELECT id FROM users WHERE id=?', (random_id, )).fetchone():
        random_id = random.randint(100000, 999999)
    query = f'INSERT INTO "users" ("id","username","password", "role") VALUES (?, ?, ?, "user");'
    cursor.execute(query, (random_id, login, settings.hashlib.md5(password.encode()).hexdigest(), ))
    conn.commit()
    query = f'SELECT id FROM users WHERE username=?'
    result = cursor.execute(query, (login, )).fetchone()
    conn.commit()
    queries = [f'INSERT INTO sessions ("id") VALUES ({result[0]})',
               f'UPDATE users SET session_id={result[0]} WHERE username="{login}"']
    settings.multiple_queries_to_db(queries, cursor, conn)
    cursor.close()
    return 1, f'Новый пользователь {login} зарегистрирован!'