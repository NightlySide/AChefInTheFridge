import difflib
import os

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from databaserw import RecettesDB, IngredientsDB, Ingredient, Recette
from userdata import load_ing_list, save_ing_list

UPLOAD_FOLDER = "static/imgs"
ALLOWED_EXTENSIONS = {"png", "jpg"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "3lh47vw__at-1nAOQ61vsA"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

recettes = RecettesDB("db/recettes.json")
ingredients = IngredientsDB("db/ingredients.json")
ing_list = load_ing_list()
recettes_to_show = []


@app.route("/", methods=["POST", "GET"])
@app.route("/index.html", methods=["POST", "GET"])
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
    return render_template("index.html", recettes=recettes_to_show, ing_list=ing_list)


def search():
    global recettes_to_show
    scores = recettes.get_scores(ing_list)
    recettes_to_show = []
    for k in range(len(recettes)):
        recettes_to_show.append((recettes[k], scores[k]))
    recettes_to_show.sort(key=lambda x: x[1], reverse=True)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results = difflib.get_close_matches(search, ingredients.name_list(), n=5, cutoff=0.3)
    return jsonify(matching_results=results)


@app.context_processor
def context_processor():
    return dict()


@app.route("/add-ingredient.html", methods=["POST", "GET"])
def add_ingredient():
    if request.method == "POST":
        ing_name = request.form.get("ing_name")
        category = request.form.getlist("category")

        if ingredients.get_ingredient_by_name(ing_name, cutoff=0.8) is not None:
            # TODO : envoyer un message d'erreur sur le site
            print("ATTENTION : ingrédient en doublon on enregistre pas")
            print(ingredients.get_ingredient_by_name(ing_name, cutoff=0.8).nom)
        else:
            ing = Ingredient(ing_name, category)
            ingredients.add_item(ing)
            ingredients.write_to_db()
    return render_template("add-ingredient.html")


@app.route("/add-recette.html", methods=["POST", "GET"])
def add_recette():
    if request.method == "POST":
        rec_name = request.form.get("rec_name")
        if recettes.get_recette_by_name(rec_name, cutoff=0.8) is not None:
            # TODO : envoyer un message d'erreur sur le site
            print("ATTENTION : recette en doublon on enregistre pas")
            print(recettes.get_recette_by_name(rec_name, cutoff=0.8).nom)
        else:
            rec_ingredients = []
            rec_img = ""
            ing_list = request.form.get("ingredients").split(",")
            for ing_name in ing_list:
                if ing_name not in ["", " "]:
                    ing = ingredients.get_ingredient_by_name(ing_name)
                    if ing is None:
                        print(f"ATTENTION : L'ingrédient \"{ing_name}\" n'a pas été trouvé !")
                        # TODO : faire message d'erreur sur le site
                        return render_template("add-recette.html")
                    else:
                        rec_ingredients.append(ing)
            rec_url = request.form.get("rec_url")

            # check if the post request has the file part
            if 'rec_img' not in request.files:
                print("ATTENTION: Aucun fichier détecté dans la requete")
                rec_img = ""
            else:
                file = request.files["rec_img"]
                if file.filename == "":
                    print("ATTENTION: Aucun fichier n'a été spécifié")
                    rec_img = ""
                elif file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(os.getcwd(), app.config["UPLOAD_FOLDER"], filename)
                    file.save(save_path)
                    resize_and_crop(save_path)
                    print(f"Image {filename} sauvegardée!")
                    rec_img = os.path.join("../", app.config["UPLOAD_FOLDER"], filename)

            recette = Recette(rec_name, rec_ingredients, rec_img, rec_url)
            recettes.ajoute_recette(recette)
            recettes.write_to_db()
    return render_template("add-recette.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def resize_and_crop(file_path):
    max_size = 512
    try:
        img = Image.open(file_path)
        ratio = max(max_size / img.size[0], max_size / img.size[1])
        img = img.resize((int(ratio * img.size[0]), int(ratio * img.size[1])), Image.ANTIALIAS)
        background = Image.new("RGBA", (max_size, max_size), (255,255,255,0))
        background.paste(img, ((max_size - img.size[0]) // 2, (max_size - img.size[1]) // 2))
        background.save(file_path, "PNG")
    except IOError as e:
        print(f"Impossible de traiter l'image : {file_path}\n{str(e)}")


@app.route("/edit-ingredient.html", methods=["GET", "POST"])
def edit_ingredient():
    if request.method == "GET":
        ing_name = request.args.get("ing")
        if ing_name in [None, ""] or ingredients.get_ingredient_by_name(ing_name, cutoff=0.8) is None:
            return render_template("list-ingredients.html", ingredients=ingredients)
        else:
            ing = ingredients.get_ingredient_by_name(ing_name, cutoff=0.8)
            return render_template("edit-ingredient.html", ing=ing)
    elif request.method == "POST":
        ing_name = request.form.get("ing_name")
        category = request.form.getlist("category")

        if ingredients.get_ingredient_by_name(ing_name, cutoff=0.8) is not None:
            # TODO : envoyer un message d'erreur sur le site
            ingredients.remove(ingredients.get_ingredient_by_name(ing_name, cutoff=0.8))
            ing = Ingredient(ing_name, category)
            ingredients.add_item(ing)
            ingredients.write_to_db()
        else:
            print("ATTENTION : modification d'un ingrédient qui n'existe pas !")
        return render_template("list-ingredients.html",  ingredients=ingredients)


@app.route("/edit-recette.html", methods=["GET", "POST"])
def edit_recette():
    if request.method == "GET":
        rec_name = request.args.get("rec")
        if rec_name in [None, ""] or recettes.get_recette_by_name(rec_name, cutoff=0.8) is None:
            return render_template("list-recettes.html", recettes=recettes)
        else:
            rec = recettes.get_recette_by_name(rec_name, cutoff=0.8)
            return render_template("edit-recette.html", rec=rec)
    elif request.method == "POST":
        rec_name = request.form.get("rec_name")
        if recettes.get_recette_by_name(rec_name, cutoff=0.8) is not None:
            rec_ingredients = []
            rec_img = []
            ing_list = request.form.get("ingredients").split(",")
            for ing_name in ing_list:
                if ing_name not in ["", " "]:
                    ing = ingredients.get_ingredient_by_name(ing_name)
                    if ing is None:
                        print(f"ATTENTION : L'ingrédient \"{ing_name}\" n'a pas été trouvé !")
                        # TODO : faire message d'erreur sur le site
                        return render_template(f"edit-recette.html", rec=recettes.get_recette_by_name(rec_name))
                    else:
                        rec_ingredients.append(ing)
            rec_url = request.form.get("rec_url")

            # check if the post request has the file part
            if 'rec_img' not in request.files:
                print("ATTENTION: Aucun fichier détecté dans la requete")
                rec_img = request.form.get("original_img_path")
            else:
                file = request.files["rec_img"]
                if file.filename == "":
                    print("INFO: Aucun fichier n'a été spécifié, on conserve l'image originale")
                    rec_img = request.form.get("original_img_path")
                elif file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(os.getcwd(), app.config["UPLOAD_FOLDER"], filename)
                    file.save(save_path)
                    resize_and_crop(save_path)
                    print(f"Image {filename} sauvegardée!")
                    rec_img = os.path.join("../", app.config["UPLOAD_FOLDER"], filename)

            recettes.remove(recettes.get_recette_by_name(rec_name))
            recette = Recette(rec_name, rec_ingredients, rec_img, rec_url)
            recettes.ajoute_recette(recette)
            recettes.write_to_db()
        else:
            print("ATTENTION : modification d'une recette qui n'existe pas !")
        return render_template("list-recettes.html", recettes=recettes)


if __name__ == "__main__":
    app.run(debug=True)
