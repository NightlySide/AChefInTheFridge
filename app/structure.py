import base64


def normalize(nom):
    return nom.encode("utf8").decode()


class Recette:
    def __init__(self, id, nom, type_repas, ingredients, substituts, photo, url):
        self.id = int(id)
        self.nom = normalize(nom)
        self.type_repas = type_repas
        self.ingredients = ingredients
        self.substituts = substituts
        self.photo = photo
        self.url = normalize(url)

    def ajoute_ingredient(self, ing):
        if ing.id not in [ing.id for ing in self.ingredients]:
            self.ingredients.append(ing)
        else:
            print(f"ATTENTION : ingrédient {ing.nom} ({ing.id}) en double")

    def __eq__(self, other):
        return self.nom == other.nom

    def show_ingredients(self):
        return ", ".join([ing.nom for ing in self.ingredients])

    def est_substituable(self, ing):
        for sub_name in self.substituts:
            if sub_name == ing.nom:
                return True
        return False

    def get_base64_image(self):
        return base64.b64encode(self.photo).decode()

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


class Ingredient:
    GLUCIDES = "glucides"
    LIPIDES = "lipides"
    PROTEINES = "proteines"
    FIBRES = "fibres"
    LEGUMES = "legumes"
    EPICES = "epice"
    AUTRES = "autres"

    def __init__(self, id, nom, category=[]):
        self.id = int(id)
        self.nom = normalize(nom)
        self.category = category
        self.quantite = None

    def __eq__(self, other):
        return self.nom == other.nom

    def set_quantity(self, qte, qte_type):
        self.quantite = Quantite(qte, qte_type)


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

    def convert(self, q_type, qte=None):
        if qte is None:
            norm = self.normalise()
        else:
            norm = qte
        if q_type == Quantite.GRAMME:
            return norm
        elif q_type == Quantite.C_CAFE:
            return norm / 0.5
        elif q_type == Quantite.C_SOUPE:
            return norm / 15
        elif q_type == Quantite.PINCEE:
            return norm / 0.5
        elif q_type == Quantite.UNITE:
            return norm / 55  # oeuf = 55g/unite
        elif q_type == Quantite.GOUSSE:
            return norm / 5
        elif q_type == Quantite.GOUTTE:
            return norm / 0.000014
        elif q_type == Quantite.CENTILITRE:
            return norm / 10
        # Si le type n'est pas reconnu (ou que c'est une feuille)
        else:
            return self.qte

    def __add__(self, other):
        s = self.normalise() + other.normalise()
        return Quantite(self.convert(self.type, s), self.type)
