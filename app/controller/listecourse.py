import pdfkit

from flask import Blueprint, render_template, request, send_file

from app.sql_db import recettes
from app.structure import Quantite

bp = Blueprint("listecourse", __name__, url_prefix='/listecourse')


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


@bp.route("/faire-pdf.html", methods=["GET"])
def make_pdf():
    pdfkit.from_url("https://a-chef-in-the-frige.herokuapp.com/index.html" "liste-courses.pdf")
    return send_file("../liste-courses.pdf")
