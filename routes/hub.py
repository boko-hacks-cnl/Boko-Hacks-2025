from flask import Blueprint, redirect, render_template, session, url_for

hub_bp = Blueprint("hub", __name__)


@hub_bp.route("/hub")
def hub():
    if "user" in session:
        return render_template("hub.html", username=session["user"])
    else:
        return redirect(url_for("login.login"))
