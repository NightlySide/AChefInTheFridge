import json
from difflib import get_close_matches


def normalize(nom):
    return nom.encode().decode()


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


class Ingredient:
    GLUCIDES = "glucides"
    LIPIDES = "lipides"
    PROTEINES = "proteines"
    FIBRES = "fibres"
    LEGUMES = "legumes"
    EPICES = "epice"

    def __init__(self, nom, category=[]):
        self.nom = normalize(nom)
        self.category = category
        self.quantite = None

    def __eq__(self, other):
        return self.nom == other.nom

    def set_quantity(self, qte, qte_type):
        self.quantite = Quantite(qte, qte_type)


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
            ingredients = []
            substituts = {}
            for ing in recette.ingredients:
                ingredients.append([ing.nom, ing.quantite.qte, ing.quantite.type])
            for sub in recette.substituts:
                ings = []
                for ing in recette.substituts[sub]:
                    ings.append(ing.nom)
                substituts[sub] = ings
            data.append({"nom": nom, "img": img_path, "ingredients": ingredients, "substituts": substituts,
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


class Recette:
    def __init__(self, nom, ingredients, substituts, photo, url):
        self.nom = normalize(nom)
        self.ingredients = ingredients
        self.substituts = substituts
        self.photo = photo
        self.url = normalize(url)

    def ajoute_ingredient(self, ing):
        if ing.nom not in [ing.nom for ing in self.ingredients]:
            self.ingredients.append(ing)
        else:
            print(f"ATTENTION : ingrédient {ing.nom} en double")

    def __eq__(self, other):
        return self.nom == other.nom

    def show_ingredients(self):
        return ", ".join([ing.nom for ing in self.ingredients])

    def est_substituable(self, ing):
        for sub_name in self.substituts:
            if sub_name == ing.nom:
                return True
        return False

    def get_substituts(self, sub_name):
        if sub_name not in self.substituts:
            print(f"ERREUR : le substitut {sub_name} pas trouvé dans la recette {self.nom}")
            return None
        return ", ".join([ing.nom for ing in self.substituts[sub_name]])

    def ingredient_dans_recette(self, ing, ing_list):
        if ing.nom in self.substituts:
            for sub in self.get_substituts(ing.nom).split(","):
                if sub in [ing.nom for ing in ing_list]:
                    return True
        if ing in ing_list:
            return True
        return False

    def get_score(self, ing_list):
        score = 0
        total = 0
        if len(self.ingredients) == 0:
            return 0
        for ing in self.ingredients:
            if self.ingredient_dans_recette(ing, ing_list):
                score += ing.quantite.normalise()
            total += ing.quantite.normalise()

        score = round((score / total) * 100)
        return score


class Quantite:
    GRAMME = "gramme"
    GOUSSE = "gousse"
    PINCEE = "pincee"
    CENTILITRE = "centilitre"
    C_SOUPE = "csoupe"
    C_CAFE = "ccafe"
    GOUTTE = "goutte"
    UNITE = "unite"
    FEUILLE = "feuille"

    QTE_TYPES = [GRAMME, GOUSSE, PINCEE, CENTILITRE, C_SOUPE, C_CAFE, GOUTTE, UNITE, FEUILLE]

    def __init__(self, qte, qte_type):
        if qte_type not in self.QTE_TYPES:
            print(f"ATTENTION : type de quantité non reconnu '{qte_type}'")
        self.type = qte_type
        self.qte = int(qte)

    def normalise(self):
        if self.type == Quantite.GRAMME:
            return self.qte
        elif self.type == Quantite.C_CAFE:
            return self.qte * 0.5
        elif self.type == Quantite.C_SOUPE:
            return self.qte * 15
        elif self.type == Quantite.PINCEE:
            return self.qte * 0.5
        elif self.type == Quantite.UNITE:
            return self.qte * 55  # oeuf = 55g/unite
        elif self.type == Quantite.GOUSSE:
            return self.qte * 5
        elif self.type == Quantite.GOUTTE:
            return self.qte * 0.000014
        elif self.type == Quantite.CENTILITRE:
            return self.qte * 10
        # Si le type n'est pas reconnu (ou que c'est une feuille)
        else:
            return 0

    def __str__(self):
        if self.type == Quantite.GRAMME:
            return str(self.qte) + "g"
        elif self.type == Quantite.GOUSSE:
            return f"{self.qte} Gousses" if self.qte > 1 else f"{self.qte} Gousse"
        elif self.type == Quantite.PINCEE:
            return f"{self.qte} Pincées" if self.qte > 1 else f"{self.qte} Pincée"
        elif self.type == Quantite.CENTILITRE:
            return f"{self.qte}cl"
        elif self.type == Quantite.C_SOUPE:
            return f"{self.qte} c.à.s."
        elif self.type == Quantite.C_CAFE:
            return f"{self.qte} c.à.c."
        elif self.type == Quantite.GOUTTE:
            return f"{self.qte} Gouttes" if self.qte > 1 else f"{self.qte} Goutte"
        elif self.type == Quantite.FEUILLE:
            return f"{self.qte} Feuilles" if self.qte > 1 else f"{self.qte} Feuille"
        else:
            return str(self.qte)


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
