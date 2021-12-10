from os import path, unlink
from secrets import token_hex

from flask import redirect, url_for, flash
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView, form
from wtforms.validators import NumberRange
from flask_login import current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

from hbestore.database import db
from hbestore.models import User, Brand, Category, Color, Size, Product, Photo, Request
from hbestore.utils import format_image, formatar_moeda_real


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

                    new_photo = Photo(name, photo.filename)

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

                new_photo = Photo(name, photo.filename)

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


class RequestView(ModelView):
    def user_name(self, request, pedido, *args):
        user = User.query.get(pedido.user_id)
        return user.first_name.capitalize()

    def user_email(self, request, pedido, *args):
        user = User.query.get(pedido.user_id)
        return user.email

    def produtos(self, request, pedido, *args):
        li = []
        for purchase in pedido.purchases:
            p = Product.query.get(purchase.product_id)
            li.append(f"(ID-{p.id}; Total={purchase.amount})")

        
        return li

    can_edit = False
    can_delete = False


    column_list = ["id", "value_total", "form_of_payment", "created_on", "user", "item"]

    column_labels = {
        "id": "Nº Pedido",
        "value_total": "Valor Final R$",
        "form_of_payment": "Forma de Pagamento",
        "created_on": "Data da Compra",
        "user": "Cliente",
        "item": "Produtos",
    }


    column_formatters = {
        "value_total": lambda self, request, pedido, *args: formatar_moeda_real(pedido.value_total),
        "user": user_name,
        "item": produtos,
        "created_on": lambda self, request, pedido, *args: pedido.created_on.strftime('%d/%m/%Y %H:%M'),
    }

    column_default_sort = ("created_on", True)


class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        return redirect(url_for('home.index'))


admin = Admin(index_view=MyAdminIndexView())
upload = None

def init_app(app):
    global upload
    upload = app.config["UPLOAD_FOLDER"]
    admin.name = "HBestore administração"
    admin.template_mode = "bootstrap4"
    admin.add_view(AnalyticsView(name="Site", endpoint="analytics"))
    admin.add_view(UserView(User, db.session, "Usuário"))
    admin.add_view(BrandView(Brand, db.session, "Marca"))
    admin.add_view(BrandView(Category, db.session, "Categoria"))
    admin.add_view(BrandView(Color, db.session, "Cor"))
    admin.add_view(BrandView(Size, db.session, "Tamanho"))
    admin.add_view(ProductView(Product, db.session, "Produto"))
    admin.add_view(RequestView(Request, db.session, "Pedidos"))
    admin.init_app(app)
