from os import getenv, path, curdir


def init_app(app):
    app.config["SECRET_KEY"] = "saoisdjasdjisadjiosdjioasjdoijdsoidj"

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://sndtgdrhmpjydj:77d54bfd5d41ee323d1a75ea41b75cc5800e870a62aeecaccd50d82b6f57ca90@ec2-18-210-159-154.compute-1.amazonaws.com:5432/d6bbeskjsqeo8e"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = "hagab.estore@gmail.com"
    app.config["MAIL_PASSWORD"] = "batatinhafrita123"

    app.config["UPLOAD_FOLDER"] = path.join(
        path.abspath(curdir),
        "hbestore/static/img/products"
    )
    app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png"]
