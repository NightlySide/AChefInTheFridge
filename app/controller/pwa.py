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
