from flask import Blueprint, render_template, session, request, redirect, flash, url_for
from flask_mail import Message

from hbestore.models import Product
from hbestore.mail import mail
from hbestore.utils import formatar_moeda_real, calcular_estoque


home = Blueprint("home", __name__)


def init_app(app):
    app.register_blueprint(home)


@home.route("/<ordenar>")
@home.route("/")
def index(ordenar=None):
    buscar = request.args.get("buscar", None)
    if buscar:
        buscar = buscar.strip().lower()
    if ordenar == "menor":
        produtos = Product.query.order_by(Product.price.asc()).all()
    elif ordenar == "maior":
        produtos = Product.query.order_by(Product.price.desc()).all()
    elif ordenar == "lancamentos":
        produtos = Product.query.order_by(Product.id.desc()).all()
    elif buscar:
        produtos = Product.query.filter(Product.name.like(f"%{buscar}%")).all()
    else:
        produtos = Product.query.all()

    products = []
    for p in produtos:
        if len(p.photos) > 0:
            if ordenar == "feminino" or ordenar == "masculino":
                if p.category.name.lower() == ordenar:
                    dict_product = {}
                    dict_product["id"] = p.id
                    dict_product["name"] = p.name.lower()
                    dict_product["brand"] = p.brand.name.capitalize() if p.brand else ""
                    dict_product["category"] = p.category.name.capitalize() if p.category else ""
                    dict_product["size"] = p.size.name.upper() if p.size else ""
                    dict_product["color"] = p.color.name.capitalize() if p.color else ""
                    dict_product["price"] = formatar_moeda_real(p.price)
                    dict_product["description"] = p.description.lower()
                    dict_product["stock"] = calcular_estoque(session, p.id, p.stock)
                    dict_product["photo"] = p.photos[0].name
                    products.append(dict_product)
            else:
                dict_product = {}
                dict_product["id"] = p.id
                dict_product["name"] = p.name.lower()
                dict_product["brand"] = p.brand.name.capitalize() if p.brand else ""
                dict_product["category"] = p.category.name.capitalize() if p.category else ""
                dict_product["size"] = p.size.name.upper() if p.size else ""
                dict_product["color"] = p.color.name.capitalize() if p.color else ""
                dict_product["price"] = formatar_moeda_real(p.price)
                dict_product["description"] = p.description
                dict_product["stock"] = calcular_estoque(session, p.id, p.stock)
                dict_product["photo"] = p.photos[0].name
                products.append(dict_product)
    return render_template("index.html", products=products, title="Página Inicial")


@home.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html", title="Contato")
    
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    try:
        msg = Message(
            subject="Contato pelo site",
            sender="hagab.estore@gmail.com",
            recipients=["hagab.estore@gmail.com",],
            html=f'''
            Mensagem enviada por:<br>
            <b>{name} {email}</b><br>

            {message}
            '''
        )
        mail.send(msg)
    except:
        flash("Não foi possível enviar a mensagem", "danger")
        return redirect(url_for("home.contact"))
    else:
        flash("Mensagem enviada com sucesso", "success")
        return redirect(url_for("home.confirm_contact"))


@home.route("/confirm-contac")
def confirm_contact():
    return render_template("confirm-contact.html")
