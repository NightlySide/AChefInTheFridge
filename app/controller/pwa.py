from flask import Blueprint, send_from_directory, make_response, send_file

bp = Blueprint("pwa", __name__, url_prefix='')


@bp.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')


@bp.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'js/sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response


@bp.route("/recettes.json")
def download_recettes():
    return send_file("../db/recettes.json", as_attachment=True)


@bp.route("/ingredients.json")
def download_ingredients():
    return send_file("../db/ingredients.json", as_attachment=True)

@bp.route("/js/<filename>")
def static_script(filename):
    return send_file("static/js/"+filename)

@bp.route("/css/<filename>")
def static_stymle(filename):
    return send_file("static/css/"+filename)