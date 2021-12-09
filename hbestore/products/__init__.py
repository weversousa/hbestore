from flask import Blueprint, render_template

from hbestore.models import Product


products = Blueprint("products", __name__, url_prefix="/products")


def init_app(app):
    app.register_blueprint(products)


@products.route("/product/<int:id>")
def product(id=None):
    p = Product.query.get(id)
    product = {}
    product["id"] = p.id
    product["name"] = p.name
    product["price"] = p.price
    product["description"] = p.description
    product["photo_main"] = p.photos[0].name
    product["photos"] = [photo.name for photo in p.photos]
    return render_template("product.html", product=product)
