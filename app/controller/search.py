import difflib

from flask import Blueprint, render_template, request, jsonify

from app import userdata
from app.databaserw import ingredients, recettes

bp = Blueprint("search", __name__, url_prefix='/search')

ing_list = userdata.load_ing_list()
recettes_to_show = []


@bp.route("/", methods=["POST", "GET"])
@bp.route("/index.html", methods=["POST", "GET"])
def index():
    global ing_list, recettes_to_show
    if request.method == "POST":
        ing_name = request.form.get("add-ingredient")
        ing = ingredients.get_ingredient_by_name(ing_name)
        if ing is None:
            print("Ingrédient non reconnu !")
            # TODO : afficher une erreur sur la page web
        else:
            ing_list.append(ing)
            userdata.save_ing_list(ing_list)
    elif request.method == "GET":
        rtype = request.args.get("type")
        if rtype == "remove_ing":
            ing_name = request.args.get("id")
            ing = ingredients.get_ingredient_by_name(ing_name)
            if ing is None:
                print(f"Ingrédient non présent dans la BDD : \"{ing_name}\"")
                # TODO : afficher une erreur sur la page web
            elif ing not in ing_list:
                print(f"Ingrédient non trouvé dans la liste : \"{ing_name}\"")
                # TODO : afficher une erreur sur la page web
            else:
                ing_list.remove(ing)
        elif rtype == "search":
            scores = recettes.get_scores(ing_list)
            recettes_to_show = []
            for k in range(len(recettes)):
                recettes_to_show.append((recettes[k], scores[k]))
            recettes_to_show.sort(key=lambda x: x[1], reverse=True)
    return render_template("search/index.html", recettes=recettes_to_show, ing_list=ing_list)


@bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results = difflib.get_close_matches(search, ingredients.name_list(), n=5, cutoff=0.3)
    return jsonify(matching_results=results)