from settings import *
from utils import *


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(HTTPException)
def not_found(error):
    print(f'[-] {error}')
    return redirect('/'), 302


@app.route("/")
def index():
    context_login = False
    username = validate_session(request.cookies.get('session'))
    if username:
        context_login = True
    context_admin = validate_role(request.cookies.get('session'), 'admin')
    context_support = validate_role(request.cookies.get('session'), 'support')
    context = {"login": context_login, "username": username, "admin": [context_admin, FLAG_AUTH],
               'posts': get_posts(), "support": [context_support, FLAG_BRUTEHASH]}
    res = make_response(render_template("index.html", context=context))
    return res


@app.route("/instruction", methods=["GET"])
def instruction():
    context_login = False
    username = validate_session(request.cookies.get('session'))
    if username:
        context_login = True
    context_support = validate_role(request.cookies.get('session'), 'support')
    content = read_file(request.values.get('lang'))
    context = {"login": context_login, "username": username, "support": context_support, "content": content}
    context_admin = validate_role(request.cookies.get('session'), 'admin')
    context["admin"] = [context_admin, FLAG_AUTH]
    context["path_to_file"] = f"/tmp/{PT_FILE}"
    return make_response(render_template("instruction.html", context=context))


@app.route("/status", methods=["GET", "POST"])
def status():
    context_login = False
    username = validate_session(request.cookies.get('session'))
    context_admin = validate_role(request.cookies.get('session'), 'admin')
    if username:
        context_login = True
    context = {"login": context_login, "username": username, "admin": [context_admin, FLAG_AUTH]}
    if request.method == "GET":
        return make_response(render_template("status.html", context=context))
    else:
        if context_admin:
            try:
                result = requests.get(f'http://{request.values.get('server')}:6177/some_api_for_checker_status')
                return result.text
            except Exception as err:
                return str(err)
        else:
            return redirect('/'), 403


@app.route("/some_api_for_checker_status", methods=["GET"])
def ok():
    return 'OK'


@app.route("/search", methods=["POST"])
def search():
    context_login = False
    username = validate_session(request.cookies.get('session'))
    if username:
        context_login = True
    context_admin = validate_role(request.cookies.get('session'), 'admin')
    context_support = validate_role(request.cookies.get('session'), 'support')
    data = request.form
    if 'filter' not in data:
        return redirect("/")
    posts, msg = search_posts(request.form.get('filter'), request.form.get('search'))
    if msg:
        pass
    context = {"login": context_login, "username": username, "admin": [context_admin, FLAG_AUTH],
               'posts': posts, "support": context_support, "msg": msg}
    return make_response(render_template("index.html", context=context))


@app.route('/posts/<post_id>', methods=["GET", "POST"])
def post(post_id):
    context = {}
    context_login = False
    username = validate_session(request.cookies.get('session'))
    if username:
        context_login = True
        context["username"] = username
    context_admin = validate_role(request.cookies.get('session'), 'admin')
    context["admin"] = [context_admin, FLAG_AUTH]
    context["login"] = context_login
    context["post_id"] = post_id
    comments = get_comments_from_post(post_id)
    context['comments'] = comments
    info_post = get_post(post_id)
    context['post'] = {"author": info_post[1], "title": info_post[2], "tags": info_post[3].split(','),
                       "path": info_post[4]}
    if request.method == "GET":
        return render_template('post.html', context=context)
    else:
        if username != request.form.get("author"):
            return make_response(render_template("post.html", context=context))
        add_comment_to_post(post_id, request.form.get("author"), request.form.get("comment"))
        return redirect(f'/posts/{post_id}')


@app.route('/create', methods=["GET", "POST"])
def new_post():
    context_login = False
    username = validate_session(request.cookies.get('session'))
    if username:
        context_login = True
    context_admin = validate_role(request.cookies.get('session'), 'admin')
    context = {"login": context_login, "username": username, "admin": [context_admin, FLAG_AUTH], "msg": ""}
    if request.method == "GET":
        return make_response(render_template("add_post.html", context=context))
    else:
        if not context_login:
            return make_response(render_template("add_post.html", context=context))
        info_post = request.form.to_dict()
        info_post['username'] = username
        is_ok, msg = upload_file(request.files['file'], info_post)
        context['msg'] = msg
        return make_response(render_template("add_post.html", context=context))


@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    context = {}
    context_admin = validate_role(request.cookies.get('session'), 'admin')
    context["admin"] = [context_admin, FLAG_AUTH]
    if request.method == "GET":
        if validate_session(request.cookies.get('session')):
            return make_response(redirect('/'))
        context['msg'] = msg
        return make_response(render_template("login.html", context=context))
    else:
        time.sleep(1.5)
        is_ok, new_session, msg = validate_login(request.form.get('login'), request.form.get('password'))
        if is_ok:
            res = make_response(redirect('/'))
            res.set_cookie("session", new_session, httponly=True, samesite="Strict")
            res.set_cookie("BotCookie", "I'm not the bot!", httponly=False, samesite="Strict")
            payload = jwt.decode(new_session, SECRET_KEY, algorithms="HS256")
            res.set_cookie("refresh_token", payload['refresh_token'], httponly=False, samesite="Strict")
            res.set_cookie("expired", str(payload['expired']), httponly=False, samesite="Strict")
            res.set_cookie("user_id", str(payload['user_id']), httponly=False, samesite="Strict")
            return res
        else:
            context['msg'] = msg
            return make_response(render_template("login.html", context=context))


@app.route("/logout", methods=['GET'])
def logout():
    if validate_session(request.cookies.get('session')):
        delete_session(request.cookies.get('session'))
    res = make_response(redirect('/'))
    res.delete_cookie("session")
    return res


@app.route("/api/refresh", methods=['POST'])
def refresh():
    if validate_session(request.cookies.get('session')):
        data = request.json
        is_ok, new_session = refresh_token(request.cookies.get('session'), data['refresh_token'], data['user_id'])
        if is_ok:
            res = make_response()
            res.set_cookie("session", new_session, httponly=True, samesite="Strict")
            payload = jwt.decode(new_session, SECRET_KEY, algorithms="HS256")
            res.set_cookie("refresh_token", payload['refresh_token'], httponly=False, samesite="Strict")
            res.set_cookie("expired", str(payload['expired']), httponly=False, samesite="Strict")
            res.set_cookie("user_id", str(payload['user_id']), httponly=False, samesite="Strict")
            return res
        else:
            res = make_response(redirect('/'))
            res.delete_cookie("session")
            return res
    res = make_response(redirect('/'))
    res.delete_cookie("session")
    return res


@app.route("/register", methods=['GET', 'POST'])
def register():
    context = {'msg': None}
    context_admin = validate_role(request.cookies.get('session'), 'admin')
    context["admin"] = [context_admin, FLAG_AUTH]
    if request.method == "GET":
        if validate_session(request.cookies.get('session')):
            return redirect('/')
        return make_response(render_template("register.html", context=context))
    else:
        is_ok, msg = validate_registration(request.form.get('login'), request.form.get('password'),
                                           request.form.get('confirm_password'))
        context['msg'] = msg
        return make_response(render_template("register.html", context=context))


if __name__ == "__main__":
    prepare()
    app.run(host=host, port=port)
