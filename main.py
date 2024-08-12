from settings import *


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    res = make_response(render_template("index.html"))
    return res


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return make_response(render_template("login.html"))
    else:
        print(request.form['login'])
        print(request.form['password'])
        return make_response(render_template("login.html"))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return make_response(render_template("register.html"))
    else:
        return make_response(render_template("register.html"))
