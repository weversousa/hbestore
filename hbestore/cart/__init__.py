from math import ceil

from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import login_required, current_user
from flask_mail import Message, smtplib
from requests import get

from hbestore.models import Product, Request, Purchase
from hbestore.database import db
from hbestore.utils import formatar_moeda_real
from hbestore.mail import mail


cart = Blueprint("cart", __name__, url_prefix="/cart")


def init_app(app):
    app.register_blueprint(cart)


@cart.route("/add/product/<int:id>")
@login_required
def add_product(id=None):
    id = str(id)
    if id not in session["cart"]:
        session["cart"][id] = 1
    else:
        session["cart"].pop(id)
    session.modified = True
    return redirect(url_for("home.index"))


@cart.route("list/products")
def list_products():
    cart = list(session["cart"].keys())
    products = []
    total_value = 0.0
    for product in Product.query.filter(Product.id.in_(cart)):
        p = {}
        id = str(product.id)
        p["id"] = id
        p["name"] = product.name.capitalize()
        p["description"] = product.description
        p["stock"] = product.stock
        p["photo"] = product.photos[0].name
        p["price"] = formatar_moeda_real(product.price)
        total_item = session["cart"][id] * product.price
        p["total_item"] = formatar_moeda_real(total_item)
        total_value += float(total_item)
        products.append(p)

    total_value = formatar_moeda_real(f"{total_value:.2f}")
    return render_template("cart.html", products=products, total_value=total_value, title="Produtos")


@cart.route("/remove/product/<int:id>")
@login_required
def remove_product(id=None):
    id = str(id)
    try:
        if id in session["cart"]:
            session["cart"].pop(id, None)
            session.modified = True
    except KeyError as e:
        pass
    finally:
        return redirect(url_for("cart.list_products"))


@cart.route("/amount/product/<int:id>/<arrow>/<int:stock>")
@cart.route("/amount/product/<int:id>/<arrow>")
@login_required
def amount_product(id=None, arrow=None, stock=0):
    id = str(id)
    if arrow == "+":
        if not session["cart"][id] == stock:
            session["cart"][id] += 1
    elif arrow == "-":
        if not session["cart"][id] == 1:
            session["cart"][id] -= 1
    session.modified = True
    return redirect(url_for("cart.list_products"))


@cart.route("/checkout/products")
@login_required
def checkout_products():
    cart = list(session["cart"].keys())
    products = []
    total_value = 0.0
    for product in Product.query.filter(Product.id.in_(cart)):
        p = {}
        id = str(product.id)
        p["id"] = id
        p["name"] = product.name.capitalize()
        p["description"] = product.description
        p["stock"] = product.stock
        p["photo"] = product.photos[0].name
        p["price"] = formatar_moeda_real(product.price)
        total_item = session["cart"][id] * product.price
        p["total_item"] = formatar_moeda_real(total_item)
        total_value += float(total_item)
        products.append(p)

    session["total_value"] = f"{total_value:.2f}"
    total_value = formatar_moeda_real(f"{total_value:.2f}")
    return render_template("checkout-products.html", products=products, total_value=total_value, title="Confirmação de Produtos")


@cart.route("/checkout/address", methods=["GET", "POST"])
@login_required
def checkout_address():
    if request.method == "GET":
        address = get(f"https://viacep.com.br/ws/{current_user.adresses.zip_code}/json/").json()
        address["numero"] = current_user.adresses.number
        address["reference"] = current_user.adresses.reference
        address["complement"] = current_user.adresses.complement
        return render_template("checkout-address.html", address=address, title="Endereço")
    else:
        return redirect(url_for("cart.checkout_payment"))


@cart.route("/checkout/payment", methods=["GET", "POST"])
@login_required
def checkout_payment():
    if request.method =="GET":
        total_value = formatar_moeda_real(session["total_value"])
        parcelas = {}
        parcelas["um"] = total_value
        parcelas["dois"] = formatar_moeda_real(f'{(float(session["total_value"]) / 2):.2f}')
        parcelas["tres"] = formatar_moeda_real(f'{(float(session["total_value"]) / 3):.2f}')
        parcelas["quatro"] = formatar_moeda_real(f'{(float(session["total_value"]) / 4):.2f}')
        parcelas["cinco"] = formatar_moeda_real(f'{(float(session["total_value"]) / 5):.2f}')
        parcelas["seis"] = formatar_moeda_real(f'{(float(session["total_value"]) / 6):.2f}')
        min_value = ceil(float(session["total_value"]))
        return render_template("checkout-payment.html", total_value=total_value, parcelas=parcelas, title="Pagamento", min_value=min_value)
    else:
        troco = request.form["troco"]
        if troco != "":
            troco = formatar_moeda_real(f'{troco.replace(",", ".")}')
            pedido = Request(current_user.id, current_user.adresses.zip_code, current_user.adresses.number, f"Dinheiro: R$ {troco}", float(session["total_value"]))
        else:
            installments = request.form["installments"]
            pedido = Request(current_user.id, current_user.adresses.zip_code, current_user.adresses.number, f"Cartão: {installments}", float(session["total_value"]))

        db.session.add(pedido)
        db.session.commit()

        for id, amount in session["cart"].items():
            db.session.add(Purchase(current_user.id, pedido.id, id, amount))
            product = Product.query.get(id)
            product.stock -= amount
            db.session.commit()

        return redirect(url_for("cart.checkout_request", pedido=pedido.id))


@cart.route("/checkout/request/<pedido>")
def checkout_request(pedido):
    try:
        mail.send(Message(
            subject="Compra aprovada",
            sender="hagab.estore@gmail.com",
            recipients=[current_user.email,],
            body=f'''
            O seu pedido foi realizado com sucesso:

            Nº pedido: {pedido}

            Todos os detalhes do pedido você encontra em:
            Minha Conta na área do Cliente.
            '''
        ))
    except Exception:
        pass

    session["cart"] = dict()
    session.pop("total_value", None)
    return render_template("checkout-request.html", pedido=pedido, title="Número do Pedido")
