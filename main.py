import difflib

from flask import Flask, render_template, request, session, jsonify
from databaserw import RecettesDB, IngredientsDB
from userdata import load_ing_list, save_ing_list

app = Flask(__name__)
app.config["SECRET_KEY"] = "3lh47vw__at-1nAOQ61vsA"

recettes = RecettesDB("db/recettes.json")
ingredients = IngredientsDB("db/ingredients.json")
ing_list = load_ing_list()
recettes_to_show = []


@app.route("/", methods=["POST", "GET"])
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
            save_ing_list(ing_list)
            search()
    if request.method == "GET":
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
            search()
    return render_template("index.html")


def search():
    global recettes_to_show
    scores = recettes.get_scores(ing_list)
    recettes_to_show = []
    for k in range(len(recettes)):
        recettes_to_show.append((recettes[k], scores[k]))


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results = difflib.get_close_matches(search, ingredients.name_list(), cutoff=0.3)
    return jsonify(matching_results=results)


@app.context_processor
def context_processor():
    rec = recettes.get_recette_by_name("gratin de chou-fleur")
    return dict(recettes=recettes_to_show, ing_list=ing_list)


if __name__ == "__main__":
    app.run(debug=True)
