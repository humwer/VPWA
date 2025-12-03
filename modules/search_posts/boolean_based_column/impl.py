from utils import *


def search_posts(column, value) -> list:
    data = []

    try:
        conn, cursor = connect_to_db()
        if "'" in value or ";" in value:
            raise Exception("[?] Крутят скулю в поиске")
        if ";" in column or "union" in column.lower():
            raise Exception("[?] Крутят скулю в фильтре и пытаются сделать stacked/union")
        query = f"SELECT * FROM posts WHERE {column} like '%{value}%';"
        posts = cursor.execute(query, ).fetchall()
        cursor.close()
        for post in posts:
            data.append({'id': post[0], 'author': post[1], 'title': post[2],
                         'tags': post[3].split(','), 'path': post[4], 'visible': post[5]})
        return sorted(data, key=lambda x: x['id'], reverse=True)

    except Exception as err:
        print(f"[?] {err}")
        return data