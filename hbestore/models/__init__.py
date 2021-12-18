from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from hbestore.database import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)

    sign_up = db.relationship("SignUp", uselist=False, cascade="all, delete")
    adresses = db.relationship("Address", uselist=False, cascade="all, delete")
    requests = db.relationship("Request")

    def __init__(self, email, first_name, last_name, password, admin=False):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = self.criptografar_password(password)
        self.admin = admin

    def criptografar_password(self, password):
        return generate_password_hash(password)

    def descriptografar_password(self, password):
        return check_password_hash(self.password, password)


class SignUp(db.Model):
    __tablename__ = "sign_up"

    id = db.Column(db.Integer, primary_key=True)
    birth = db.Column(db.Date, nullable=False)
    sex = db.Column(db.String(1), nullable=False)
    cell_phone = db.Column(db.String(11), nullable=False)
    fixed_phone = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, birth, sex, cell_phone, fixed_phone):
        self.birth = birth
        self.sex = sex
        self.cell_phone = cell_phone
        self.fixed_phone = fixed_phone


class Address(db.Model):
    __tablename__ = "adresses"

    id = db.Column(db.Integer, primary_key=True)
    zip_code = db.Column(db.String(8), nullable=False)
    number = db.Column(db.String(5), nullable=False)
    complement = db.Column(db.String(30))
    reference = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    db.UniqueConstraint(zip_code, number, user_id)

    def __init__(self, zip_code, number, complement=None, reference=None, user_id=None):
        self.zip_code = zip_code
        self.number = number
        self.complement = complement
        self.reference = reference
        self.user_id = user_id


class Brand(db.Model):
    __tablename__ = "brands"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def __repr__(self):
        return f"{self.name}"


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def __repr__(self):
        return f"{self.name}"

class Color(db.Model):
    __tablename__ = "colors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def __repr__(self):
        return f"{self.name}"

class Size(db.Model):
    __tablename__ = "sizes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def __repr__(self):
        return f"{self.name}"

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(5,2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String)
    created_on = db.Column(db.DateTime, default=datetime.now)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    color_id = db.Column(db.Integer, db.ForeignKey("colors.id"))
    size_id = db.Column(db.Integer, db.ForeignKey("sizes.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    db.UniqueConstraint(name, brand_id, category_id, color_id, size_id)

    brand = db.relationship("Brand", uselist=False)
    category = db.relationship("Category", uselist=False)
    color = db.relationship("Color", uselist=False)
    size = db.relationship("Size", uselist=False)
    photos = db.relationship("Photo", cascade="all, delete")

    def __init__(self, name, price, stock, description, brand_id, category_id, color_id, size_id, user_id):
        self.name = name
        self.price = price
        self.stock = stock
        self.description = description
        self.brand_id = brand_id
        self.category_id = category_id
        self.color_id = color_id
        self.size_id = size_id
        self.user_id = user_id


class Photo(db.Model):
    __tablename__ = "photos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))

    def __init__(self, name):
        self.name = name


class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    zip_code = db.Column(db.String(8), nullable=False)
    number = db.Column(db.String(5), nullable=False)
    form_of_payment = db.Column(db.String(50), nullable=False)
    value_total = db.Column(db.Numeric(5,2), nullable=False)
    shipping = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, default=datetime.now)
    shipping_on = db.Column(db.DateTime, default=None)

    purchases = db.relationship("Purchase")

    def __init__(self, user_id, zip_code, number, form_of_payment, value_total):
        self.user_id = user_id
        self.zip_code = zip_code
        self.number = number
        self.form_of_payment = form_of_payment
        self.value_total = value_total


class Purchase(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, user_id, request_id, product_id, amount):
        self.user_id = user_id
        self.request_id = request_id
        self.product_id = product_id
        self.amount = amount
