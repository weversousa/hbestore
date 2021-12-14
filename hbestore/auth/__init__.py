from uuid import uuid4

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_wtf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from flask_mail import Message

from hbestore.models import User, SignUp, Address
from hbestore.database import db
from hbestore.mail import mail


auth = Blueprint("auth", __name__, url_prefix="/auth")
csrf = CSRFProtect()
login_manager = LoginManager()

def init_app(app):
    app.register_blueprint(auth)
    csrf.init_app(app)
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def handle_needs_login():
    return redirect(url_for("auth.sign_in", next_page=request.endpoint))


@auth.route("/sign-in", methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    if request.method == "GET":
        return render_template("sign-in.html", title="Entrar")

    email = request.form["email"].lower()
    password = request.form["password"].strip()
    user = User.query.filter(User.email == email).first()

    if not user:
        flash("Esse e-mail não existe.", "email")
        return redirect(url_for("auth.sign_in"))

    if not user.descriptografar_password(password):
        flash("A senha está errada.", "password")
        return redirect(url_for("auth.sign_in"))

    login_user(user)

    if "cart" not in session:
        session["cart"] = dict()

    if "endpoint" in session:
        return redirect(url_for(session["endpoint"]))
    return redirect(url_for("home.index"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "GET":
        return render_template("sign-up.html", title="Cria Conta")

    first_name = request.form["firstName"].strip().lower()
    last_name = request.form["lastName"].strip().lower()
    birth = request.form["birth"]
    sex = request.form["sex"]
    email = request.form["email"].strip().lower()
    cell_phone = request.form["cellPhone"].strip().lower()
    fixed_phone = request.form["fixedPhone"].strip().lower()
    zip_code = request.form["zipCode"].strip()
    number = request.form["number"].strip()
    complement = request.form["complement"].strip()
    reference = request.form["reference"].strip()
    password = request.form["password"].strip()
    password_confirm = request.form["passwordConfirm"].strip()

    if User.query.filter(User.email == email).first():
        flash("E-mail já existe. Favor tentar recuperar a senha.", "email")
        return redirect(url_for("auth.sign_up"))

    if password != password_confirm:
        flash("As senhas não são iguais.", "password")
        return redirect(url_for("auth.sign_up"))

    new_user = User(email, first_name, last_name, password)
    new_sign_up = SignUp(birth, sex, cell_phone, fixed_phone)
    new_address = Address(zip_code, number, complement, reference)
    new_user.sign_up = new_sign_up
    new_user.adresses = new_address

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Erro ao tentara salvador os dados.", "usuario")
        return redirect(url_for("auth.sign_up"))
    else:
        flash("Registrado com sucesso.", "success")
        return redirect(url_for("auth.sign_in"))


@auth.route("/recover-password", methods=["GET", "POST"])
def recover_password():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))


    if request.method == "GET":
        return render_template("recover-password.html", title="Recuperar Senha")

    email = request.form["email"].strip().lower()
    user = User.query.filter(User.email == email).first()

    if not user:
        flash("E-mail não existe.", "email")
        return redirect(url_for("auth.recover_password"))

    new_password = uuid4().hex
    user.password = user.criptografar_password(new_password)
    db.session.commit()

    try:
        msg = Message(
            subject="Recuperação de senha",
            sender="hagab.estore@gmail.com",
            recipients=[email, ],
            body=f'''
            Olá, {user.first_name.capitalize()}
            Sua nova senha:
            {new_password}

            Você pode alterar essa senha através da área do cliente.
            '''
        )
        mail.send(msg)
    except:
        pass
    return redirect(url_for('auth.confirm_recover_password', email=email))


@auth.route("/confirm-recover-password/<email>")
def confirm_recover_password(email=None):
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    return render_template("confirm-recover-password.html", email=email, title="Confirmação de Recuperação de Senha")


@auth.route('logout')
@login_required
def logout():
    logout_user()
    session.pop("cart")
    return redirect(url_for('auth.sign_in'))
