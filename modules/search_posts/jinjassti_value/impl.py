from utils import *

'''
SSTI Injection (Jinja) при поиске в параметре search
'''


def search_posts(column, value) -> tuple:
    data = []

    try:
        conn, cursor = settings.connect_to_db()
        like_pattern = f'%{value}%'
        if column != "title" and column != "tags" and column != "username":
            return data, "Что-то пошло не так..."
        query = f"SELECT * FROM posts WHERE {column} like ?;"
        posts = cursor.execute(query, (like_pattern, )).fetchall()
        cursor.close()
        for post in posts:
            data.append({'id': post[0], 'author': post[1], 'title': post[2],
                         'tags': post[3].split(','), 'path': post[4], 'visible': post[5]})
        if data:
            return sorted(data, key=lambda x: x['id'], reverse=True), ""
        for exclude in settings.app.EXCLUDE_FOR_SSTI:
            if exclude in value:
                return sorted(data, key=lambda x: x['id'], reverse=True), f"Не-не-не, никаких RCE :)"
        return sorted(data, key=lambda x: x['id'], reverse=True), f"Не был найден пост с {settings.render_template_string(value)}"

    except Exception as err:
        print(f"[?] {err}")
        return data, ""