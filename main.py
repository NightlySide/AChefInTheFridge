from flask import Flask, render_template, request, session
from databaserw import RecettesDB, IngredientsDB
from userdata import load_ing_list, save_ing_list

app = Flask(__name__)
app.config["SECRET_KEY"] = "3lh47vw__at-1nAOQ61vsA"

recettes = RecettesDB("db/recettes.json")
ingredients = IngredientsDB("db/ingredients.json")
ing_list = load_ing_list()


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        ing_name = request.form.get("add-ingredient")
        ing = ingredients.get_ingredient_by_name(ing_name)
        if ing is None:
            print("Ingrédient non reconnu !")
            # TODO : afficher une erreur sur la page web
        else:
            ing_list.append(ing)
            save_ing_list(ing_list)
    if request.method == "GET":
        rtype = request.args.get("type")
        if rtype == "remove_ing":
            ing_name = request.args.get("id")
            ing = ingredients.get_ingredient_by_name(ing_name)
            if ing is None:
                print(f"Ingrédient non présent dans la BDD : \"{ing_name}\"")
            elif ing not in ing_list:
                print(f"Ingrédient non trouvé dans la liste : \"{ing_name}\"")
            else:
                ing_list.remove(ing)
    return render_template("index.html")


@app.context_processor
def context_processor():
    rec = recettes.get_recette_by_name("gratin de chou-fleur")
    return dict(recettes=recettes, ing_list=ing_list)


if __name__ == "__main__":
    app.run(debug=True)
