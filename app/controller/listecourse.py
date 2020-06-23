import os
import subprocess

import pdfkit

from flask import Blueprint, render_template, request, make_response

from app.sql_db import recettes
from app.structure import Quantite

bp = Blueprint("listecourse", __name__, url_prefix='/listecourse')


def _get_pdfkit_config():
    """wkhtmltopdf lives and functions differently depending on Windows or Linux. We
     need to support both since we develop on windows but deploy on Heroku.

    Returns:
        A pdfkit configuration
    """
    WKHTMLTOPDF_CMD = subprocess.Popen(['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')],
                                       stdout=subprocess.PIPE).communicate()[0].strip()
    return pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)


@bp.route("/")
@bp.route("/index.html", methods=["GET"])
def index():
    rec_sel = {}
    ing_qte = []
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    for jour in jours:
        for k in range(3):
            if jour + "-" + str(k) in request.args:
                rec_sel[jour + "-" + str(k)] = request.args.get(jour + "-" + str(k))
    for rec_id in rec_sel.values():
        if rec_id != "":
            rec = recettes.get_recette_by_id(int(rec_id))
            for ing in rec.ingredients:
                for k in range(len(ing_qte)):
                    if ing_qte[k][0].id == ing.id:
                        ing_qte[k][1] += ing.quantite
                        break
                else:
                    ing_qte.append([ing, Quantite(ing.quantite.qte, ing.quantite.type)])
    ing_qte.sort(key=lambda x: x[0].nom)

    return render_template("listecourse/index.html", recettes=recettes, rec_sel=rec_sel, ing_list=ing_qte)


@bp.route("/faire-pdf.html", methods=["POST"])
def make_pdf():
    data = []
    for ing_name in request.form:
        data.append((ing_name, request.form.get(ing_name)))

    html = render_template("listecourse/pdf_template.html", data=data, path=request.url_root[:-1])

    # config = pdfkit.configuration(wkhtmltopdf='./bin/wkhtmltopdf')
    pdf = pdfkit.from_string(html, False, configuration=_get_pdfkit_config())

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=liste-de-courses.pdf"

    return response
