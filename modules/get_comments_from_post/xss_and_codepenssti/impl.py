from utils import *

'''
SSTI (псевдо-Codepen) и XSS (с фильтром <script>) в комментариях к постам
'''


def get_comments_from_post(post_id: str) -> list:
    conn, cursor = settings.connect_to_db()
    query = f'SELECT * FROM comments WHERE post_id=?'
    comments = cursor.execute(query, (post_id, )).fetchall()
    data = []
    for comment in comments:
        query = f'SELECT id FROM users WHERE username=?'
        if comment[2] != 'support':
            user_id = cursor.execute(query, (comment[2],)).fetchone()[0]
        else:
            user_id = 'Support - птица гордая'
        try:
            msg = comment[3]
            codepen_templ = settings.re.search(r"#{[A-Za-z0-9.*]*}", msg)
            if codepen_templ:
                pseudo_jinja = settings.render_template_string("{{"+codepen_templ.group()[2:-1]+"}}")
                msg = msg[:codepen_templ.start()] + pseudo_jinja + msg[codepen_templ.end():]
            if '<script>' in msg.lower():
                data.append({'username': comment[2], 'user_id': user_id,
                             'msg': "<i>Обнаружен вредоносный комментарий!</i>"})
            else:
                data.append({'username': comment[2], 'msg': msg, 'user_id': user_id})
        except Exception as err:
            data.append({'username': comment[2], 'user_id': user_id,
                         'msg': "<i>Возникла ошибка при формировании комментария</i>"})
    cursor.close()
    return data
