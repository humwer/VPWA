from utils import *


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
            user_id = 'Ищи другой путь'
        try:
            groovy_templ = settings.re.search(r"\${[A-Za-z0-9.*]*}", comment[3])
            if groovy_templ:
                pseudo_jinja = settings.render_template_string("{{"+groovy_templ.group()[2:-1]+"}}")
                data.append({'username': comment[2], 'msg': comment[3][:groovy_templ.start()] + pseudo_jinja +
                                                            comment[3][groovy_templ.end():], 'user_id': user_id})
            else:
                data.append({'username': comment[2], 'msg': comment[3], 'user_id': user_id})
        except Exception as err:
            data.append({'username': comment[2], 'user_id': user_id,
                         'msg': settings.render_template_string("<i>Возникла ошибка при формировании комментария</i>")})
    cursor.close()
    return data
