from os import unlink
from secrets import token_hex

from flask import redirect, url_for, jsonify
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView, form
from flask_admin.menu import MenuLink
from wtforms.validators import NumberRange
from flask_login import current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

from hbestore.database import db
from hbestore.models import User, Brand, Category, Color, Size, Product, Photo, Request
from hbestore.utils import format_image, formatar_moeda_real, via_cep2


class MyAdminIndexView(AdminIndexView):
    def is_visible(self):
        return False

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.sign_in'))


class UserView(ModelView):
    column_list = ("email", "first_name", "last_name", "admin", "created_on")
    column_labels = {
        "email": "E-mail",
        "first_name": "Nome",
        "last_name": "Sobrenome",
        "password": "Senha",
        "admin": "Administrador",
        "created_on": "Criado em"
    }
    form_excluded_columns = ["sign_up", "created_on", "adresses", "requests"]

    column_formatters = {
        "created_on": lambda self, request, user, *args: user.created_on.strftime('%d/%m/%Y %H:%M'),
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.sign_in'))

    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password)
        return super().on_model_change(form, model, is_created)


class BrandView(ModelView):
    column_list = ["name", "created_on"]
    column_labels = {"name": "Nome", "created_on": "Criado em"}
    form_excluded_columns = ["created_on"]
    column_formatters = {
        "name": lambda self, request, brand, *args: brand.name.upper(),
        "created_on": lambda self, request, brand, *args: brand.created_on.strftime('%d/%m/%Y %H:%M'),
    }


class ProductView(ModelView):
    def on_model_change(self, form, model, is_created):
        if not is_created:
            try:
                for photo in model.photos:
                    unlink("hbestore/static/img/products/" + photo.name)
            except (IndexError, FileNotFoundError):
                pass

            photos = model.photo

            try:
                for photo in photos:
                    ext = secure_filename(photo.filename).split(".")[1]
                    name = f"{token_hex(30)}.{ext}"
                    photo.save("hbestore/static/img/products/" + name)

                    format_image("hbestore/static/img/products/" + name)

                    new_photo = Photo(name)

                    model.photos.append(new_photo)
            except (IndexError, FileNotFoundError):
                pass
            return super().on_model_change(form, model, is_created)

        photos = model.photo

        try:
            for photo in photos:
                ext = secure_filename(photo.filename).split(".")[1]
                name = f"{token_hex(30)}.{ext}"
                photo.save("hbestore/static/img/products/" + name)

                format_image("hbestore/static/img/products/" + name)

                new_photo = Photo(name)

                model.photos.append(new_photo)
        except (IndexError, FileNotFoundError):
            pass
        return super().on_model_change(form, model, is_created)

    def on_model_delete(self, model):
        try:
            for photo in model.photos:
                unlink("hbestore/static/img/products/" + photo.name)
        except (IndexError, FileNotFoundError):
            pass
        return super().on_model_delete(model)

    column_list = ["id", "name", "price", "stock", "description", "brand", "category", "color", "size", "created_on"]

    column_labels = {
        "id": "ID",
        "name": "Nome",
        "price": "Preço",
        "stock": "Estoque",
        "description": "Descrição",
        "brand": "Marca",
        "category": "Categoria",
        "color": "Cor",
        "size": "Tamanho",
        "created_on": "Criado em",
    }

    column_searchable_list = ["id"]

    form_excluded_columns = ["photos", "created_on"]

    form_columns = ["name", "price", "stock", "brand", "category", "color", "size", "description", "photo"]

    form_overrides = dict(
        description=form.fields.TextAreaField,
        price=form.fields.DecimalField
    )

    form_extra_fields = {
        "photo": form.fields.MultipleFileField("Fotos")
    }

    form_args = dict(
        stock=dict(validators=[NumberRange(min=1, max=100)]),
        price=dict(validators=[NumberRange(min=0.00, max=999.99)])
    )

    column_formatters = {
        "name": lambda self, request, product, *args: product.name.upper() if product else product,
        "description": lambda self, request, product, *args: product.description.upper() if product.description else product.description,
        "brand": lambda self, request, product, *args: product.brand.name.upper() if product.brand else product.brand,
        "category": lambda self, request, product, *args: product.category.name.upper() if product.category else product.category,
        "color": lambda self, request, product, *args: product.color.name.upper() if product.color else product.color,
        "size": lambda self, request, product, *args: product.size.name.upper() if product.size else product.size,
        "created_on": lambda self, request, product, *args: product.created_on.strftime('%d/%m/%Y %H:%M'),
    }


def client_name(id):
    user = User.query.get(id)
    return user.first_name + " " + user.last_name


class RequestView(BaseView):
    @expose("/")
    def index(self):
        pedidos = []    
        for pedido in Request.query.all():
            dict_pedido = {}
            dict_pedido["date"] = pedido.created_on.strftime('%d/%m/%Y')
            dict_pedido["id"] = pedido.id
            dict_pedido["value_total"] = 0.0
            dict_pedido["form_of_payment"] = pedido.form_of_payment
            dict_pedido["client"] = client_name(pedido.user_id)
            dict_pedido["address"] = via_cep2(pedido.zip_code, pedido.number)
            dict_pedido["shipping"] = "glyphicon glyphicon-remove" if not pedido.shipping else "glyphicon glyphicon-ok"
            dict_pedido["products"] = []
            for obj_produto in pedido.purchases:
                produto = Product.query.get(obj_produto.product_id)
                dict_produto = {}
                dict_produto["id"] = produto.id
                dict_produto["color"] = produto.color.name
                dict_produto["size"] = produto.size.name
                dict_produto["brand"] = produto.brand.name
                dict_produto["name"] = produto.name.capitalize()
                dict_produto["price"] = formatar_moeda_real(produto.price)
                dict_produto["amount"] = obj_produto.amount
                dict_produto["subtotal"] = formatar_moeda_real(produto.price * obj_produto.amount)
                dict_pedido["value_total"] += float(produto.price * obj_produto.amount)
                dict_pedido["products"].append(dict_produto)
            dict_pedido["value_total"] = formatar_moeda_real(f'{dict_pedido["value_total"]:.2f}')
            pedidos.append(dict_pedido)
        return self.render('admin-requests.html', pedidos=pedidos)


class RequestShippingView(ModelView):
    can_edit = True
    can_delete = False
    can_create = False

    column_list = ["id", "shipping"]

    column_labels = {
        "id": "Nº Pedido",
        "shipping": "Enviado"
    }

    column_searchable_list = ["id"]


class HomeMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(index_view=MyAdminIndexView())
upload = None

def init_app(app):
    global upload
    upload = app.config["UPLOAD_FOLDER"]
    admin.name = "HBestore administração"
    admin.template_mode = "bootstrap3"
    admin.add_view(UserView(User, db.session, "Usuário"))
    admin.add_view(BrandView(Brand, db.session, "Marca"))
    admin.add_view(BrandView(Category, db.session, "Categoria"))
    admin.add_view(BrandView(Color, db.session, "Cor"))
    admin.add_view(BrandView(Size, db.session, "Tamanho"))
    admin.add_view(ProductView(Product, db.session, "Produto"))
    admin.add_view(RequestView(name="Pedidos", endpoint="requets-shipping"))
    admin.add_view(RequestShippingView(Request, db.session, "Envio dos Pedidos"))
    admin.add_link(HomeMenuLink(name="Páginia Inicial", url="/"))
    admin.add_link(LogoutMenuLink(name="Sair", url="/auth/logout"))
    admin.init_app(app)
