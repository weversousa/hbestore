from flask import Flask

from hbestore import config, babel, database, home, auth, admin, products, cart, client, mail


def create_app():
    app = Flask(__name__)
    config.init_app(app)
    babel.init_app(app)
    database.init_app(app)
    home.init_app(app)
    auth.init_app(app)
    admin.init_app(app)
    products.init_app(app)
    cart.init_app(app)
    client.init_app(app)
    mail.init_app(app)
    return app
