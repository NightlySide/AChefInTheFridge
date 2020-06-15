from difflib import get_close_matches
from cryptography.fernet import Fernet
from base64 import b64decode

import MySQLdb as mbd
import requests
import json

from app.structure import Ingredient, Recette


def sql_request(query):
    rows = []
    key = b"vM7QeIoY3sdxDpRI0jAbnRk8vUbsGHb0VfZ12YhpfRg="
    cred_url = b64decode("""aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9OaWdodGx5U2lkZS80YzU5YzBhOTExN2
                            FkNzI4NjcwNDEwNmJhN2NiYjc3NC9yYXcvNTc1OTA2Zjc3YjI3Y2MxNzkyNDM4YTdiNGRjNWQwMTBi
                            MWNhZmYyYy9hLWNoZWYtaW4tdGhlLWZyaWRnZS1jcmVk""").decode()
    creds = requests.get(cred_url).text
    conn = mbd.connect(user=Fernet(key).decrypt(creds.split("&")[0].encode()).decode(),
                       password=Fernet(key).decrypt(creds.split("&")[1].encode()).decode(),
                       host="ieta-docs.ddns.net", port=33006,
                       database="achefinthefridge")

    cursor = conn.cursor()
    cursor.execute(query)

    for row in cursor:
        rows.append(row)

    cursor.close()
    conn.close()

    return rows


class IngredientsDB(list):
    def __init__(self):
        super(IngredientsDB, self).__init__()
        rows = sql_request("SELECT * from ingredients")
        for row in rows:
            id, nom, category = row
            self.append(Ingredient(id, nom, category.split(",")))

    def write_to_db(self):
        pass

    def name_list(self):
        return [ing.nom for ing in self]

    def id_list(self):
        return [ing.id for ing in self]

    def add_item(self, ing):
        if ing.id not in self.id_list():
            self.append(ing)

    def get_ingredient_by_name(self, nom, cutoff=0.8):
        match = get_close_matches(nom, self.name_list(), cutoff=cutoff)
        if len(match) == 0:
            return None
        for ing in self:
            if ing.nom == match[0]:
                return ing
        return None

    def get_ingredient_by_id(self, ing_id):
        for ing in self:
            if ing.id == ing_id:
                return ing
        return None

    def sort_by_name(self):
        return sorted(self, key=lambda x: x.nom)


class RecettesDB(list):
    def __init__(self):
        super(RecettesDB, self).__init__()
        rows = sql_request("SELECT * FROM recettes")
        ing_db = IngredientsDB()
        for row in rows:
            id, nom, img_path, ing_list, sub_list, url = row
            ingredients = []
            substituts = {}
            for ing_name, qte, qte_type in json.loads(ing_list):
                ing = ing_db.get_ingredient_by_name(ing_name)
                if ing is None:
                    raise Exception(f"ERREUR : ingrédient \"{ing_name}\" non trouvé dans la recette \"{nom}\"")
                ing.set_quantity(qte, qte_type)
                ingredients.append(ing)
            if sub_list != "":
                for sub_name in json.loads(sub_list):
                    if ing_db.get_ingredient_by_name(sub_name) is None:
                        raise Exception(f"ERREUR : ingrédient \"{sub_name}\" comme substitut dans \"{nom}\"")
                    sub = []
                    for ing_name in json.loads(sub_list)[sub_name]:
                        ing = ing_db.get_ingredient_by_name(ing_name)
                        if ing is None:
                            raise Exception(f"ERREUR : ingrédient \"{ing_name}\" non trouvé dans les substituts de la "
                                            f"recette \"{nom}\"")
                        sub.append(ing)
                    substituts[sub_name] = sub
            self.append(Recette(id, nom, ingredients, substituts, img_path, url))

    def write_to_db(self):
        pass

    def name_list(self):
        return [rec.nom for rec in self]

    def id_list(self):
        return [rec.id for rec in self]

    def ajoute_recette(self, rec):
        if rec.id not in self.id_list():
            self.append(rec)

    def get_recette_by_name(self, nom, cutoff=0.6):
        match = get_close_matches(nom, self.name_list(), cutoff=cutoff)
        if len(match) == 0:
            return None
        for rec in self:
            if rec.nom == match[0]:
                return rec
        return None

    def get_recette_by_id(self, rec_id):
        for rec in self:
            if rec.id == rec_id:
                return rec
        return None

    def sort_by_name(self):
        return sorted(self, key=lambda x: x.nom)

    def get_scores(self, ing_list):
        return [rec.get_score(ing_list) for rec in self]


ingredients = IngredientsDB()
recettes = RecettesDB()

if __name__ == "__main__":
    ingredients = IngredientsDB()
    recettes = RecettesDB()
    print(recettes.name_list())
    print("Done")
