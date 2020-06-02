from flask import Blueprint, send_from_directory, make_response

bp = Blueprint("pwa", __name__, url_prefix='')


@bp.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')


@bp.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'js/sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response
