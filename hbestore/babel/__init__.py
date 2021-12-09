from flask_babelex import Babel


babel = Babel()


def init_app(app):
    babel._default_locale = "pt_BR"
    babel.init_app(app)
