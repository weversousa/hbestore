from flask import Blueprint, render_template, session

from hbestore.models import Product
from hbestore.utils import formatar_moeda_real, calcular_estoque


products = Blueprint("products", __name__, url_prefix="/products")


def init_app(app):
    app.register_blueprint(products)


@products.route("/product/<int:id>")
def product(id=None):
    p = Product.query.get(id)
    product = {}
    product["id"] = p.id
    product["name"] = p.name
    product["brand"] = p.brand.name.capitalize() if p.brand else ""
    product["size"] = p.size.name.upper() if p.size else ""
    product["color"] = p.color.name.capitalize() if p.color else ""
    product["price"] = formatar_moeda_real(f"{p.price:.2f}")
    product["description"] = p.description
    product["stock"] = calcular_estoque(session, p.id, p.stock)
    product["photo_main"] = p.photos[0].name
    product["photos"] = [photo.name for photo in p.photos]
    return render_template("product.html", product=product, title="Produto")
