from settings import *
from utils import *


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


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
