from flask import Flask

from app.controller import edit, listecourse, search, pwa, main

# Création et configuration de l'application
app = Flask(__name__)
app.config["SECRET_KEY"] = "3lh47vw__at-1nAOQ61vsA"
app.config["UPLOAD_FOLDER"] = "app/static/imgs"

# On enregistre les blueprints
app.register_blueprint(main.bp)
app.register_blueprint(edit.bp)
app.register_blueprint(listecourse.bp)
app.register_blueprint(search.bp)
app.register_blueprint(pwa.bp)
