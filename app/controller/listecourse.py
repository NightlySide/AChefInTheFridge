from flask import Blueprint, render_template

bp = Blueprint("listecourse", __name__, url_prefix='/listecourse')


@bp.route("/")
@bp.route("/index.html")
def index():
    return render_template("listecourse/index.html")