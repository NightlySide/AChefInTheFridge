import json
from difflib import get_close_matches
from app.structure import Ingredient, Recette


class IngredientsDB(list):
    def __init__(self, path="db/ingredients.json"):
        super(IngredientsDB, self).__init__()
        self.path = path
        with open(self.path, "r") as f:
            data = json.loads(f.read())
        for item in data:
            self.append(Ingredient(item["nom"], item["category"]))

    def write_to_db(self):
        data = []
        for ing in self:
            data.append({"nom": ing.nom, "category": ing.category})
        with open(self.path, "w") as f:
            f.write(json.dumps(data, indent=4))

    def name_list(self):
        return [ing.nom for ing in self]

    def add_item(self, ing):
        if ing.nom not in self.name_list():
            self.append(ing)

    def get_ingredient_by_name(self, nom, cutoff=0.8):
        match = get_close_matches(nom, self.name_list(), cutoff=cutoff)
        if len(match) == 0:
            return None
        for ing in self:
            if ing.nom == match[0]:
                return ing
        return None

    def sort_by_name(self):
        return sorted(self, key=lambda x: x.nom)


class RecettesDB(list):
    def __init__(self, path="db/recettes.json"):
        super(RecettesDB, self).__init__()
        self.path = path
        with open(self.path, "r") as f:
            data = json.loads(f.read())
        ing_db = IngredientsDB()
        for item in data:
            nom = item["nom"]
            img_path = item["img"]
            ingredients = []
            substituts = {}
            url = item["url"]
            for ing_name, qte, qte_type in item["ingredients"]:
                ing = ing_db.get_ingredient_by_name(ing_name)
                if ing is None:
                    raise Exception(f"ERREUR : ingrédient \"{ing_name}\" non trouvé dans la recette \"{nom}\"")
                ing.set_quantity(qte, qte_type)
                ingredients.append(ing)
            if "substituts" in item:
                for sub_name in item["substituts"]:
                    if ing_db.get_ingredient_by_name(sub_name) is None:
                        raise Exception(f"ERREUR : ingrédient \"{sub_name}\" comme substitut dans \"{nom}\"")
                    sub = []
                    for ing_name in item["substituts"][sub_name]:
                        ing = ing_db.get_ingredient_by_name(ing_name)
                        if ing is None:
                            raise Exception(f"ERREUR : ingrédient \"{ing_name}\" non trouvé dans les substituts de la "
                                            f"recette \"{nom}\"")
                        sub.append(ing)
                    substituts[sub_name] = sub
            self.append(Recette(nom, ingredients, substituts, img_path, url))

    def write_to_db(self):
        data = []
        for recette in self:
            nom = recette.nom
            img_path = recette.photo
            ing_list = []
            substituts = {}
            for ing in recette.ingredients:
                ing_list.append([ing.nom, ing.quantite.qte, ing.quantite.type])
            for sub in recette.substituts:
                ings = []
                for ing in recette.substituts[sub]:
                    ings.append(ing.nom)
                substituts[sub] = ings
            data.append({"nom": nom, "img": img_path, "ingredients": ing_list, "substituts": substituts,
                         "url": recette.url})
        with open(self.path, "w") as f:
            f.write(json.dumps(data, indent=4))

    def name_list(self):
        return [rec.nom for rec in self]

    def ajoute_recette(self, rec):
        if rec.nom not in self.name_list():
            self.append(rec)

    def get_recette_by_name(self, nom, cutoff=0.6):
        match = get_close_matches(nom, self.name_list(), cutoff=cutoff)
        if len(match) == 0:
            return None
        for rec in self:
            if rec.nom == match[0]:
                return rec
        return None

    def sort_by_name(self):
        return sorted(self, key=lambda x: x.nom)

    def get_scores(self, ing_list):
        return [rec.get_score(ing_list) for rec in self]


# Variable de BDD
recettes = RecettesDB("db/recettes.json")
ingredients = IngredientsDB("db/ingredients.json")

if __name__ == "__main__":
    ingDB = IngredientsDB()
    ingDB.add_item(Ingredient("Chou-fleur"))
    ingDB.add_item(Ingredient("Farine"))
    ingDB.add_item(Ingredient("Oeuf"))
    ingDB.add_item(Ingredient("Carotte"))
    ingDB.add_item(Ingredient("Beurre"))
    ingDB.add_item(Ingredient("Lait"))
    ingDB.add_item(Ingredient("Parmesan"))
    ingDB.write_to_db()

    recDB = RecettesDB()
    rec = Recette("Gratin de chou-fleur", [], {}, "")
    rec.ajoute_ingredient(ingDB.get_ingredient_by_name("chou-fleur"))
    rec.ajoute_ingredient(ingDB.get_ingredient_by_name("lait"))
    rec.ajoute_ingredient(ingDB.get_ingredient_by_name("beurre"))
    rec.ajoute_ingredient(ingDB.get_ingredient_by_name("farine"))
    recDB.ajoute_recette(rec)
    recDB.write_to_db()

    print(recDB.get_recette_by_name("gratin de chou-fleur"))
