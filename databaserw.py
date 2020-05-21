import json
from difflib import get_close_matches


class IngredientsDB(list):
    def __init__(self, path="db/ingredients.json"):
        super(IngredientsDB, self).__init__()
        self.path = path
        with open(self.path, "r") as f:
            data = json.loads(f.read())
        for item in data:
            self.append(Ingredient(item["nom"]))

    def write_to_db(self):
        data = []
        for ing in self:
            data.append({"nom": ing.nom})
        with open(self.path, "w") as f:
            f.write(json.dumps(data, indent=4))

    def name_list(self):
        return [ing.nom for ing in self]

    def add_item(self, ing):
        if ing.nom not in self.name_list():
            self.append(ing)

    def get_ingredient_by_name(self, nom):
        match = get_close_matches(nom, self.name_list())
        if len(match) == 0:
            return None
        for ing in self:
            if ing.nom == match[0]:
                return ing
        return None


class Ingredient:
    def __init__(self, nom):
        self.nom = nom

    def __eq__(self, other):
        return self.nom == other.nom
        
        
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
            for ing_name in item["ingredients"]:
                ing = ing_db.get_ingredient_by_name(ing_name)
                if ing is None:
                    raise Exception(f"ERREUR : ingrédient \"{ing_name}\" non trouvé dans la recette \"{nom}\"")
                ingredients.append(ing)
            self.append(Recette(nom, ingredients, img_path))

    def write_to_db(self):
        data = []
        for recette in self:
            nom = recette.nom
            img_path = recette.photo
            ingredients = []
            for ing in recette.ingredients:
                ingredients.append(ing.nom)
            data.append({"nom": nom, "img": img_path, "ingredients": ingredients})
        with open(self.path, "w") as f:
            f.write(json.dumps(data, indent=4))

    def name_list(self):
        return [rec.nom for rec in self]

    def ajoute_recette(self, rec):
        if rec.nom not in self.name_list():
            self.append(rec)

    def get_recette_by_name(self, nom):
        match = get_close_matches(nom, self.name_list())[0]
        for rec in self:
            if rec.nom == match:
                return rec
        return None

    def get_scores(self, ing_list):
        scores = []
        for rec in self:
            score = 0
            for ing in rec.ingredients:
                if ing in ing_list:
                    score += 1
            score = round((score / len(rec.ingredients)) * 100)
            scores.append(score)
        return scores


class Recette:
    def __init__(self, nom, ingredients, photo):
        self.nom = nom
        self.ingredients = ingredients
        self.photo = photo

    def ajoute_ingredient(self, ing):
        if ing.nom not in [ing.nom for ing in self.ingredients]:
            self.ingredients.append(ing)
        else:
            print(f"ATTENTION : ingrédient {ing.nom} en double")

    def __eq__(self, other):
        return self.nom == other.nom


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

    #print(ingDB.get_ingredient_by_name("lait").nom)

    recDB = RecettesDB()
    rec = Recette("Gratin de chou-fleur", [], "")
    rec.ajoute_ingredient(ingDB.get_ingredient_by_name("chou-fleur"))
    rec.ajoute_ingredient(ingDB.get_ingredient_by_name("lait"))
    rec.ajoute_ingredient(ingDB.get_ingredient_by_name("beurre"))
    rec.ajoute_ingredient(ingDB.get_ingredient_by_name("farine"))
    recDB.ajoute_recette(rec)
    recDB.write_to_db()

    print(recDB.get_recette_by_name("gratin de chou-fleur"))
