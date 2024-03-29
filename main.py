# Stdlib
import os, yaml

# Pip
import flask_login
from flask import Flask, render_template, request, redirect, make_response
from flask_login import login_required

# In-house
from utils import run_command_shell
from simpleusers import usermgr
from mlcmanager import mlcmgr

app = Flask(__name__)
app.secret_key = "CorrectBatteryStapleHorseLol"

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

db = usermgr()
mlc = mlcmgr()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(uid):
    if not db.check_user_exists(uid):
        return
    user = User()
    user.id = uid
    return user


@login_manager.request_loader
def request_loader(request):
    uid = request.form.get("uid")
    if not db.check_user_exists(uid):
        return
    user = User()
    user.id = uid
    return user


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":

        msg = request.cookies.get("msg")
        hmsg = ""
        if msg is not None:
            hmsg = "<p style='color:red;'>" + msg + "</p>"

        resp = make_response(
            render_template(
                "page.html",
                page_title="Login",
                content=hmsg + render_template("signin.html"),
            )
        )

        if msg is not None:
            resp.delete_cookie("msg")

        return resp
    else:
        uid = request.form["uid"]
        if db.check_user_exists(uid) and db.auth_user(uid, request.form["passwd"]):
            user = User()
            user.id = uid
            flask_login.login_user(user, remember=True)
            return redirect("/")
        else:
            resp = make_response(redirect("/login"))
            resp.set_cookie("msg", "Login failed.")
            return resp


@app.route("/logout")
def logout():
    flask_login.logout_user()
    return redirect("/")


@app.route("/")
def main():
    if not flask_login.current_user.is_authenticated:
        pc = "<a href='/login'>Login</a>"
    else:
        pc = f"<p>Hi, {flask_login.current_user.id}</p>" + render_template(
            "logout.html"
        ) + "<br/><h3>All repos:</h3>" + mlc.html_repo_list()
    return render_template("page.html", page_title="Home", content=pc)


@app.route("/repos/<name>")
@login_required
def getrepo(name):
    if not mlc.config["has_subdirs"]:
        return "This repo doesn't have subdirs. Use: TODO: new handler"
    else:
        return render_template(
            "page.html",
            page_title=f"Repo Info - {name}",
            content=mlc.html_list_packages(name),
        )


@app.route("/packages/<repo>/<name>")
@login_required
def getpackage(repo, name):
    if not mlc.config["has_subdirs"]:
        return "This repo doesn't have subdirs. Use: TODO: new handler"
    else:
        return render_template(
            "page.html",
            page_title=f"Package info - {name}",
            content=mlc.pkg_page(name, repo),
        )


@app.route("/pkgbuild/<repo>/<name>")
@login_required
def getpkgbuild(repo, name):
    if not mlc.config["has_subdirs"]:
        return "This repo doesn't have subdirs. Use: TODO: new handler"
    else:
        return render_template(
            "page.html",
            page_title=f"PKGBUILD for - {name}",
            content=f"<pre><code>{mlc.dump_pkgbuild(name, repo)}</code></pre>",
        )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6969, debug=True)
