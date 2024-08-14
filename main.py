from settings import *
from utils import *


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    context_login = False
    if validate_session(request.cookies.get('session')):
        context_login = True
    context = {"login": context_login}
    res = make_response(render_template("index.html", context=context))
    return res


@app.route("/login", methods=['GET', 'POST'])
def login():
    context = {}
    if request.method == "GET":
        if validate_session(request.cookies.get('session')):
            return make_response(redirect('/'))
        return make_response(render_template("login.html", context=context))
    else:
        is_ok, new_session = validate_login(request.form.get('login'), request.form.get('password'))
        if is_ok:
            res = make_response(redirect('/'))
            res.set_cookie("session", new_session)
            return res
        else:
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
    context = {}
    if request.method == "GET":
        if validate_session(request.cookies.get('session')):
            return redirect('/')
        return make_response(render_template("register.html", context=context))
    else:
        return make_response(render_template("register.html", context=context))


if __name__ == "__main__":
    prepare()
    app.run(host=host, port=port)
