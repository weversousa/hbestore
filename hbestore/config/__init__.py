from os import getenv, path, curdir
from dotenv import load_dotenv


load_dotenv()


def init_app(app):
    app.config["SECRET_KEY"] = getenv("SECRET_KEY")

    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = getenv("EMAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = getenv("EMAIL_PASSWORD")

    app.config["UPLOAD_FOLDER"] = path.join(
        path.abspath(curdir),
        "hbestore/static/img/products"
    )
    app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png"]
