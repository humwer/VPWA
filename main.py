from settings import *
from utils import *


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(HTTPException)
def not_found(error):
    return redirect('/'), 302


@app.route("/")
def index():
    context_login = False
    context_admin = False
    username = validate_session(request.cookies.get('session'))
    if username:
        context_login = True
    if username == 'admin':
        context_admin = True
    context = {"login": context_login, "username": username, "admin": [context_admin, app.flag_auth],
               'posts': get_posts()}
    res = make_response(render_template("index.html", context=context))
    return res


@app.route("/instruction", methods=["GET"])
def instruction():
    context_login = False
    username = validate_session(request.cookies.get('session'))
    context_support = validate_role(request.cookies.get('session'), 'support')
    if username:
        context_login = True
    content = read_file(request.values.get('lang'))
    context = {"login": context_login, "username": username, "support": context_support, "content": content}
    return make_response(render_template("instruction.html", context=context))


@app.route("/search", methods=["POST"])
def search():
    context_login = False
    context_admin = False
    username = validate_session(request.cookies.get('session'))
    if username:
        context_login = True
    if username == 'admin':
        context_admin = True
    data = request.form
    if 'filter' not in data:
        return redirect("/")
    posts = search_posts(request.form.get('filter'), request.form.get('search'))
    context = {"login": context_login, "username": username, "admin": [context_admin, app.flag_auth],
               'posts': posts}
    return make_response(render_template("index.html", context=context))


@app.route('/posts/<post_id>', methods=["GET", "POST"])
def post(post_id):
    context = {}
    context_login = False
    username = validate_session(request.cookies.get('session'))
    if username:
        context_login = True
        context["username"] = username
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
    context = {"login": context_login, "username": username}
    if request.method == "GET":
        return make_response(render_template("add_post.html", context=context))
    else:
        if not context_login:
            return make_response(render_template("add_post.html", context=context))
        info_post = request.form.to_dict()
        info_post['username'] = username
        upload_file(request.files['file'], info_post)
        return make_response(render_template("add_post.html", context=context))


@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    context = {}
    if request.method == "GET":
        if validate_session(request.cookies.get('session')):
            return make_response(redirect('/'))
        context['msg'] = msg
        return make_response(render_template("login.html", context=context))
    else:

        is_ok, new_session = validate_login(request.form.get('login'), request.form.get('password'))
        if is_ok:
            res = make_response(redirect('/'))
            res.set_cookie("session", new_session)
            return res
        else:
            msg = 'Неверный логин/пароль'
            context['msg'] = msg
            return make_response(render_template("login.html", context=context))


@app.route("/logout", methods=['GET'])
def logout():
    if validate_session(request.cookies.get('session')):
        delete_session(request.cookies.get('session'))
    res = make_response(redirect('/'))
    res.delete_cookie("session")
    return res


@app.route("/register", methods=['GET', 'POST'])
def register():
    context = {'msg': None}
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
