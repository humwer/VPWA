from utils import *


def refresh_token(jwt_token, ref_token, user_id):
    jwt_token = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")
    if jwt_token['refresh_token'] == ref_token and jwt_token['user_id'] == user_id:
        conn, cursor = connect_to_db()
        payload = generate_token(user_id, jwt_token['username'])
        new_session = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        query = f'UPDATE sessions SET session=?, refresh_token=? WHERE id=?'
        cursor.execute(query, (new_session, payload['refresh_token'], user_id))
        conn.commit()
        cursor.close()
        return 1, new_session
    else:
        return 0, ''
