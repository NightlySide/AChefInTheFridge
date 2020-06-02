import json

from app.databaserw import IngredientsDB


def load_ing_list():
    ing_db = IngredientsDB("db/ingredients.json")
    with open("db/userdata.json", "r") as f:
        data = json.loads(f.read())["ing_list"]
    res = []
    for ing_name in data:
        res.append(ing_db.get_ingredient_by_name(ing_name))
    return res


def save_ing_list(ing_list):
    data = []
    with open("db/userdata.json", "r") as f:
        data = json.loads(f.read())
    res = []
    for ing in ing_list:
        res.append(ing.nom)
    data["ing_list"] = res
    with open("db/userdata.json", "w") as f:
        f.write(json.dumps(data, indent=4))