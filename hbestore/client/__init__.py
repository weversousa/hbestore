from flask import Blueprint, render_template, request, redirect, url_for, session
from flask.helpers import flash, url_for
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from requests import get

from hbestore.database import db
from hbestore.models import Address, Product, User
from hbestore.utils import formatar_moeda_real


client = Blueprint("client", __name__, url_prefix="/client")


def init_app(app):
    app.register_blueprint(client)


@client.route("/")
@login_required
def index():
    return render_template("client.html")


@client.route("/personal-data", methods=["GET", "POST"])
@login_required
def personal_data():
    if request.method == "GET":
        return render_template("client-personal-data.html")
    
    first_name = request.form["firstName"].strip().lower()
    last_name = request.form["lastName"].strip().lower()
    birth = request.form["birth"]

    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.sign_up.birth = birth
    db.session.commit() 
    return redirect(url_for("client.personal_data"))


@client.route("/contacts", methods=["GET", "POST"])
@login_required
def contacts():
    if request.method == "GET":
        return render_template("client-contacts.html", title="Contatos")

    cell_phone = request.form["cellPhone"]
    fixed_phone = request.form["fixedPhone"]

    if cell_phone != "":
        current_user.sign_up.cell_phone = cell_phone

    if fixed_phone != "":
        current_user.sign_up.fixed_phone = fixed_phone

    db.session.commit() 
    return redirect(url_for("client.contacts"))


@client.route("/address/<change>")
@client.route("/address", methods=["GET", "POST"])
@login_required
def address(change=None):
    if request.method == "GET":
        address = get(f"https://viacep.com.br/ws/{current_user.adresses.zip_code}/json/").json()
        address["numero"] = current_user.adresses.number
        address["reference"] = current_user.adresses.reference
        address["complement"] = current_user.adresses.complement
        if change:
            session["change"] = True
        return render_template("client-address.html", address=address, title="Endereço")
    else:
        zip_code = request.form["zipCode"]
        number = request.form["number"]
        reference = request.form["reference"]
        complement = request.form["complement"]

        try:
            current_user.adresses.zip_code = zip_code
            current_user.adresses.number = number
            current_user.adresses.complement = complement
            current_user.adresses.reference = reference
            db.session.commit()
        except Exception:
            flash(f"Não foi possível alterar o endereço.", "danger")
        else:
            if not "change" in session:
                flash("Endereço alterado com sucesso", "success")
                return redirect(url_for("client.address"))
            session.pop("change", None)
            return redirect(url_for('cart.checkout_address'))


@client.route("/requests")
@login_required
def requests():
    pedidos = []
    
    for pedido in current_user.requests:
        dict_pedido = {}
        dict_pedido["date"] = pedido.created_on.strftime('%d/%m/%Y')
        dict_pedido["id"] = pedido.id
        dict_pedido["value_total"] = 0.0
        dict_pedido["form_of_payment"] = pedido.form_of_payment
        dict_pedido["products"] = []
        for obj_produto in pedido.purchases:
            produto = Product.query.get(obj_produto.product_id)
            dict_produto = {}
            dict_produto["name"] = produto.name.capitalize()
            dict_produto["price"] = formatar_moeda_real(produto.price)
            dict_produto["amount"] = obj_produto.amount
            dict_produto["subtotal"] = formatar_moeda_real(produto.price * obj_produto.amount)
            dict_pedido["value_total"] += float(produto.price * obj_produto.amount)
            dict_pedido["products"].append(dict_produto)
        dict_pedido["value_total"] = formatar_moeda_real(f'{dict_pedido["value_total"]:.2f}')
        pedidos.append(dict_pedido)
    return render_template("client-requests.html", pedidos=pedidos, title="Pedidos")


@client.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "GET":
        return render_template("client-change-password.html", title="Alterar Senha")

    password_current = request.form["passwordCurrent"]
    password = request.form["password"]
    password_2 = request.form["password_2"]


    if current_user.descriptografar_password(current_user.password):
        flash("A senha atual está errada.", "password_current")
        return redirect(url_for("client.change_password"))

    if password != password_2:
        flash("As senhas não são iguais", "password_2")
        return redirect(url_for("client.change_password"))

    try:
        current_user.password = current_user.criptografar_password(password)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Falha ao tentar aletar a senha", "danger")
    else:
        flash("Senha alterada com sucesso!", "success")
    finally:
        return redirect(url_for("client.change_password"))
