from flask import Blueprint, redirect, url_for

bp = Blueprint("main", __name__, url_prefix='')


@bp.route("/")
@bp.route("/index.html")
def index():
    print("Passing main")
    return redirect(url_for("search.index"))
