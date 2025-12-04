from utils import *

'''
Небезопасная загрузка SVG файла с видимой XXE
'''


def upload_file(file, info_post: dict) -> bool:
    if not is_valid_mimetype(file.mimetype):
        return False
    extension = file.filename.split('.')[-1]
    if not is_valid_extension(extension):
        return False
    conn, cursor = settings.connect_to_db()
    try:
        query = 'SELECT COUNT(*) FROM posts'
        num_last_post = cursor.execute(query).fetchone()[0]
        new_filename = ''.join(['content_', str(num_last_post+1), '.', extension])
        path_to_upload = os.path.normpath(settings.app.root_path) + os.path.normpath(settings.app.UPLOAD_FOLDER)
        if extension == "svg":
            data_file = file.stream.readlines()
            for line in data_file:
                if settings.PT_FILE.encode('utf-8') in line:
                    raise Exception('Этот файл не для чтения этой уязвимостью!')
                for exclude in settings.app.EXCLUDE_XXE:
                    if exclude.encode('utf-8') in line:
                        raise Exception('Сурсы ищешь? Лучше поищи другие уязвимости :)')
            doc = settings.etree.fromstring(b''.join([line for line in data_file]), settings.app.PARSER)
            svg_content = settings.etree.tostring(doc)
            file = open(os.path.join(path_to_upload, new_filename), 'wb')
            file.write(svg_content)
            file.close()
        else:
            file.save(os.path.join(path_to_upload, new_filename))
        tags = ','.join([tag.strip() for tag in info_post['tags'].split(',')])
        path_in_db = settings.app.UPLOAD_FOLDER + new_filename
        query = f'INSERT INTO "posts" ("username", "title", "tags", "content_path", "visible") VALUES (?, ?, ?, ?, 1);'
        cursor.execute(query, (info_post['username'], info_post['title'], tags, path_in_db,))
        conn.commit()
    except Exception as err:
        print(f'[-] {err}')
        cursor.close()
        return False
    return True