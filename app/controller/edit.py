import json
import os
import app

from PIL import Image
from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename

from app.sql_db import ingredients, Ingredient, recettes, Recette

bp = Blueprint("edit", __name__, url_prefix='/edit')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ["png", "jpg"]


def resize_and_crop(file_path):
    max_size = 512
    try:
        img = Image.open(file_path)
        ratio = max(max_size / img.size[0], max_size / img.size[1])
        img = img.resize((int(ratio * img.size[0]), int(ratio * img.size[1])), Image.ANTIALIAS)
        background = Image.new("RGBA", (max_size, max_size), (255, 255, 255, 0))
        background.paste(img, ((max_size - img.size[0]) // 2, (max_size - img.size[1]) // 2))
        background.save(file_path, "PNG")
    except IOError as e:
        print(f"Impossible de traiter l'image : {file_path}\n{str(e)}")


@bp.route("/")
@bp.route("/index.html")
def index():
    return render_template("edit/index.html", recettes=recettes, ingredients=ingredients)


@bp.route("/add-ingredient.html", methods=["POST", "GET"])
def add_ingredient():
    ingredients.update_content()
    if request.method == "POST":
        ing_name = request.form.get("ing_name")
        category = request.form.getlist("category")

        if ingredients.get_ingredient_by_name(ing_name, cutoff=0.8) is not None:
            # TODO : envoyer un message d'erreur sur le site
            print("ATTENTION : ingrédient en doublon on enregistre pas")
            print(ingredients.get_ingredient_by_name(ing_name, cutoff=0.8).nom)
        else:
            ing = Ingredient(ingredients.get_next_id(), ing_name, category)
            ingredients.add_item(ing)
            return render_template("edit/list-ingredients.html", ingredients=ingredients)
    return render_template("edit/add-ingredient.html")


@bp.route("/add-recette.html", methods=["POST", "GET"])
def add_recette():
    recettes.update_content()
    if request.method == "POST":
        rec_name = request.form.get("rec_name")
        if recettes.get_recette_by_name(rec_name, cutoff=0.9) is not None:
            # TODO : envoyer un message d'erreur sur le site
            print("ATTENTION : recette en doublon on enregistre pas")
            print(recettes.get_recette_by_name(rec_name, cutoff=0.8).nom)
        else:
            rec_ingredients = []
            rec_substituts = {}
            rec_img = []
            ing_list = json.loads(request.form.get("ing_list"))
            for ing_data in ing_list:
                ing_name = ing_data["nom"]
                if ing_name not in ["", " "]:
                    ing = ingredients.get_ingredient_by_name(ing_name)
                    if ing is None:
                        print(f"ATTENTION : L'ingrédient \"{ing_name}\" n'a pas été trouvé !")
                        # TODO : faire message d'erreur sur le site
                        return render_template("edit/add-recette.html")
                    else:
                        ing.set_quantity(ing_data["qte"], ing_data["qte_type"])
                        if ing_data["est_substituable"]:
                            subs = []
                            for sub_name in ing_data["substituts"]:
                                if sub_name not in ["", " "]:
                                    sub_ing = ingredients.get_ingredient_by_name(sub_name)
                                    if sub_ing is None:
                                        print(f"ATTENTION : Le substitut \"{sub_name}\" n'a pas été trouvé !")
                                        # TODO : faire message d'erreur sur le site
                                    subs.append(sub_ing)
                            rec_substituts[ing_name] = subs
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
                    save_path = os.path.join(app.app.config["ABS_UPLOAD_FOLDER"], filename)
                    file.save(save_path)
                    resize_and_crop(save_path)
                    with open(save_path, "rb") as f:
                        rec_img = f.read()
                    os.remove(save_path)
                    print(f"Image {filename} convertie et prête à envoyer!")
                    # rec_img = os.path.join(app.app.config["REL_UPLOAD_FOLDER"], filename)

            recette = Recette(recettes.get_next_id(), rec_name, rec_ingredients, rec_substituts, rec_img, rec_url)
            recettes.ajoute_recette(recette)
            return render_template("edit/list-recettes.html", recettes=recettes)
    return render_template("edit/add-recette.html")


@bp.route("/edit-ingredient.html", methods=["GET", "POST"])
def edit_ingredient():
    ingredients.update_content()
    if request.method == "GET":
        ing_id = request.args.get("ing")
        if ing_id in [None, ""] or ingredients.get_ingredient_by_id(int(ing_id)) is None:
            return render_template("edit/list-ingredients.html", ingredients=ingredients)
        else:
            ing = ingredients.get_ingredient_by_id(int(ing_id))
            return render_template("edit/edit-ingredient.html", ing=ing)
    elif request.method == "POST":
        ing_id = request.form.get("ing_id")
        ing_name = request.form.get("ing_name")
        category = request.form.getlist("category")

        if ingredients.get_ingredient_by_id(int(ing_id)) is not None:
            # TODO : envoyer un message d'erreur sur le site
            ing = Ingredient(ing_id, ing_name, category)
            ingredients.edit_item(ing)
        else:
            print("ATTENTION : modification d'un ingrédient qui n'existe pas !")
        return render_template("edit/list-ingredients.html", ingredients=ingredients)


@bp.route("/edit-recette.html", methods=["GET", "POST"])
def edit_recette():
    recettes.update_content()
    if request.method == "GET":
        rec_id = request.args.get("rec")
        if rec_id in [None, ""] or recettes.get_recette_by_id(int(rec_id)) is None:
            return render_template("edit/list-recettes.html", recettes=recettes)
        else:
            rec = recettes.get_recette_by_id(int(rec_id))
            return render_template("edit/edit-recette.html", rec=rec)
    elif request.method == "POST":
        rec_id = int(request.form.get("rec_id"))
        rec_name = request.form.get("rec_name")
        # print(json.loads(request.form.get("ing_list")))
        if recettes.get_recette_by_id(rec_id) is not None:
            rec_ingredients = []
            rec_substituts = {}
            rec_img = []
            ing_list = json.loads(request.form.get("ing_list"))
            for ing_data in ing_list:
                ing_name = ing_data["nom"]
                if ing_name not in ["", " "]:
                    ing = ingredients.get_ingredient_by_name(ing_name)
                    if ing is None:
                        print(f"ATTENTION : L'ingrédient \"{ing_name}\" n'a pas été trouvé !")
                        # TODO : faire message d'erreur sur le site
                        return render_template("edit/edit-recette.html", rec=recettes.get_recette_by_name(rec_name))
                    else:
                        ing.set_quantity(ing_data["qte"], ing_data["qte_type"])
                        if ing_data["est_substituable"]:
                            subs = []
                            for sub_name in ing_data["substituts"]:
                                if sub_name not in ["", " "]:
                                    sub_ing = ingredients.get_ingredient_by_name(sub_name)
                                    if sub_ing is None:
                                        print(f"ATTENTION : Le substitut \"{sub_name}\" n'a pas été trouvé !")
                                        # TODO : faire message d'erreur sur le site
                                    subs.append(sub_ing)
                            rec_substituts[ing_name] = subs
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
                    save_path = os.path.join(app.app.config["ABS_UPLOAD_FOLDER"], filename)
                    file.save(save_path)
                    resize_and_crop(save_path)
                    with open(save_path, "rb") as f:
                        rec_img = f.read()
                    os.remove(save_path)
                    print(f"Image {filename} sauvegardée!")
                    # rec_img = os.path.join(app.app.config["REL_UPLOAD_FOLDER"], filename)

            recette = Recette(rec_id, rec_name, rec_ingredients, rec_substituts, rec_img, rec_url)
            recettes.edit_recette(recette)
        else:
            print("ATTENTION : modification d'une recette qui n'existe pas !")
        return render_template("edit/list-recettes.html", recettes=recettes)


@bp.route("/remove-ingredient.html", methods=["GET"])
def remove_ingredient():
    ingredients.update_content()
    ing_id = request.args.get("ing")
    ing = ingredients.get_ingredient_by_id(int(ing_id))
    if ing is not None:
        ingredients.remove_item(ing)
    else:
        # TODO : afficer erreur sur le site
        pass
    return render_template("edit/list-ingredients.html", ingredients=ingredients)


@bp.route("/remove-recette.html", methods=["GET"])
def remove_recette():
    recettes.update_content()
    rec_id = request.args.get("rec")
    rec = recettes.get_recette_by_id(int(rec_id))
    if rec is not None:
        recettes.remove_recette(rec)
    else:
        # TODO : afficer erreur sur le site
        pass
    return render_template("edit/list-recettes.html", recettes=recettes)
