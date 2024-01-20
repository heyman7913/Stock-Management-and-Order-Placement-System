# ========================================================
# IMPORTS
import base64
import hashlib
import json
import os
import random
import sqlite3
import string
import calendar
import pdfkit
from time import sleep
from pathlib import Path

# from cryptography.fernet import Fernet
from flask import (
    Flask,
    render_template,
    abort,
    request,
    make_response,
    url_for,
    flash,
    Response,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, DateTime, desc
from sqlalchemy.sql import func

from email_thread import EmailSend

# ========================================================
# CONSTANTS

SECRET = "SECRET"
SERVER = "SERVER"
DEBUG = "DEBUG"
DATABASE = "DATABASE"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"
HOST = "HOST"
PORT = "PORT"
NAME = "NAME"
GET = "GET"
POST = "POST"
EXPIRE_NOW = 0
EXPIRE_1_WEEK = 60 * 60 * 24 * 7
BLANK = ""
AUTH_COOKIE_ADMIN = "auth_admin"
AUTH_COOKIE_EMP = "auth_emp"
AUTH_COOKIE_CUST = "auth_cust"

INVALID_CRED = "Invalid credentials provided !"
# ========================================================

PROJECT_DIR = Path(__file__).resolve().parent

# ========================================================
# DATABASE + APP

try:
    app = Flask(__name__)
    with open(os.path.join(PROJECT_DIR, "documents", "secret.json")) as secret:
        data = json.load(secret)
        server_stat = data[SERVER][DEBUG]
        server_host = data[SERVER][HOST]
        server_port = data[SERVER][PORT]
        server_name = data[SERVER][NAME]
        server_secret = data[SERVER][SECRET]
        if server_stat:
            DB_CON = "sqlite:///{database}.db".format(
                database=data[DATABASE][NAME],
            )
        else:
            DB_CON = "mysql://{user_name}:password:{password}@{host}:{port}/{database}".format(
                user_name=data[DATABASE][USERNAME],
                password=data[DATABASE][PASSWORD],
                host=data[DATABASE][HOST],
                port=data[DATABASE][PORT],
                database=data[DATABASE][NAME],
            )
        app.config["SECRET_KEY"] = server_secret
except Exception as e:
    print(str(e))
    raise KeyboardInterrupt
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_CON
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    db = SQLAlchemy(app)
    migrate = Migrate(app, db, command="migrate")


# ========================================================
# Models


# =========================
# Customer Models
class CustomerLogin(db.Model):
    __tablename__ = "customer_login"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    customer_details = db.relationship(
        "CustomerDetails", backref="customer_login", lazy=True, cascade="all, delete"
    )
    customer_order = db.relationship(
        "CustomerOrder", backref="customer_login", lazy=True, cascade="all, delete"
    )

    def __repr__(self):
        return f"{self.email}"


class CustomerDetails(db.Model):
    __tablename__ = "customer_details"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(String(50), nullable=False)
    last_name = db.Column(String(50), nullable=False)
    emailID = db.Column(String(100), nullable=False)
    phoneNumber = db.Column(Integer, nullable=False)
    address = db.Column(String(200), nullable=False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())

    customer_login_id = db.Column(
        db.Integer, db.ForeignKey("customer_login.id"), nullable=False
    )

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


# =========================
# Admin Models
class AdminLogin(db.Model):
    __tablename__ = "admin_login"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    admin_details = db.relationship(
        "AdminDetails", backref="admin_login", lazy=True, cascade="all, delete"
    )
    employee_login = db.relationship(
        "EmployeeLogin", backref="admin_login", lazy=True, cascade="all, delete"
    )

    def __repr__(self):
        return f"{self.email}"


class AdminDetails(db.Model):
    __tablename__ = "admin_details"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    emailID = db.Column(db.String(100), nullable=False)
    phoneNumber = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    admin_login_id = db.Column(
        db.Integer, db.ForeignKey("admin_login.id"), nullable=False
    )

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


# =========================
# Employee Models
class EmployeeLogin(db.Model):
    __tablename__ = "employee_login"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    created_by = db.Column(
        db.Integer, db.ForeignKey("admin_login.id", ondelete="SET NULL"), nullable=True
    )

    employee_details = db.relationship(
        "EmployeeDetails", backref="employee_login", lazy=True, cascade="all, delete"
    )
    employee_order = db.relationship(
        "EmployeeOrder", backref="employee_login", lazy=True, cascade="all, delete"
    )

    def __repr__(self):
        return f"{self.email}"


class EmployeeDetails(db.Model):
    __tablename__ = "employee_details"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    emailID = db.Column(db.String(100), nullable=False)
    phoneNumber = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    employee_login_id = db.Column(
        db.Integer, db.ForeignKey("employee_login.id"), nullable=False
    )

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


# =========================
# Product Models


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    available_quant = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    shelf_loc = db.Column(db.String(10), nullable=True)
    accp_return = db.Column(db.Boolean, nullable=True)
    reorder_quant = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    order_line = db.relationship(
        "OrderLine", backref="product", lazy=True, cascade="all, delete"
    )

    def __repr__(self):
        return f"{self.id} {self.name}"


# =========================
# Order Models


class OrderHead(db.Model):
    __tablename__ = "order_head"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    order_line = db.relationship(
        "OrderLine", backref="order_head", lazy=True, cascade="all, delete"
    )

    def __repr__(self):
        return f"{self.id} {self.name}"


class OrderLine(db.Model):
    __tablename__ = "order_line"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quant = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.Boolean, nullable=False)  # True -> Normal , False -> Return
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    order_head_id = db.Column(db.Integer, db.ForeignKey("order_head.id"), nullable=True)

    customer_order = db.relationship(
        "CustomerOrder", backref="order_line", lazy=True, cascade="all, delete"
    )
    employee_order = db.relationship(
        "EmployeeOrder", backref="order_line", lazy=True, cascade="all, delete"
    )

    def __repr__(self):
        return f"{self.id} {self.name}"


class CustomerOrder(db.Model):
    __tablename__ = "customer_order"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(30), nullable=False)
    delivery = db.Column(db.String(2), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    order_line_id = db.Column(
        db.Integer, db.ForeignKey("order_line.id"), nullable=False
    )
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customer_login.id"), nullable=False
    )

    def __repr__(self):
        return f"{self.id} {self.name}"


class EmployeeOrder(db.Model):
    __tablename__ = "employee_order"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    order_line_id = db.Column(
        db.Integer, db.ForeignKey("order_line.id"), nullable=False
    )
    employee_id = db.Column(
        db.Integer, db.ForeignKey("employee_login.id"), nullable=False
    )

    def __repr__(self):
        return f"{self.id} {self.name}"


class OrderStatus:
    ORDER_INCOMPLETE = "ORDER INCOMPLETE"
    ORDER_IN_PROGRESS = "ORDER IN PROGRESS"
    ORDER_COMPLETE = "ORDER COMPLETE"
    ORDER_ACCEPTED = "ORDER ACCEPTED"
    ORDER_REJECTED = "ORDER REJECTED"
    IN_PACK = "PACKAGING"
    IN_SHIP = "SHIPPING"
    COMPLETE = "COMPLETE"
    DELAY = "DELAY"


# ========================================================
# Routing


@app.route("/", methods=[GET])
def landingPage() -> str:
    req_method = request.method
    if req_method == GET:
        page_name = "landingpage.html"
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


def _redirect(destination: str, cookies: list):
    res = make_response()
    for cookie in cookies:
        res.set_cookie(cookie[0], cookie[1], cookie[2])
    res.headers["location"] = url_for(destination)
    return res


def _get_cookies(cookie_stack, names: list):
    cookies = {}
    for name in names:
        try:
            spec = cookie_stack.get(name)
        except Exception:
            spec = None
        cookies.update({name: spec})
    return cookies


# ======================
# Routing Customer


@app.route("/customer", methods=[GET])
def customer_landing_page():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user is logged in
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="customer_signin", cookies=cookies)
            return redirect, 302
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                # Existing Cookie belongs to user in DB
                cookies = [
                    [AUTH_COOKIE_CUST, req_cookies[AUTH_COOKIE_CUST], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(
                    destination="customer_OrderPlacement", cookies=cookies
                )
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="customer_signin", cookies=cookies)
                return redirect, 302

    else:
        abort(401)


class CustomerSignin:
    def __init__(self, login_id: str, password: str):
        self.login_id = login_id.upper()
        self.password = password
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password.encode("utf-8"))
        self.password = password_hash.hexdigest()[:254]


@app.route("/customer/signin", methods=[GET, POST])
def customer_signin():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user is logged in
            page_name = "customer_loginpage.html"
            path = os.path.join(page_name)
            return render_template(path)
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                # Existing Cookie belongs to user in DB
                cookies = [
                    [AUTH_COOKIE_CUST, req_cookies[AUTH_COOKIE_CUST], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(
                    destination="customer_OrderPlacement", cookies=cookies
                )
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="customer_signin", cookies=cookies)
                return redirect, 302

    elif req_method == POST:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user is logged in
            form_data = request.form
            customer_signin_ref = CustomerSignin(
                login_id=form_data["loginID"],
                password=form_data["password"],
            )

            # Check database for user
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == customer_signin_ref.login_id,
                CustomerLogin.password_hash == customer_signin_ref.password,
            ).first()
            if customer_login_db is not None:
                cookies = [
                    [AUTH_COOKIE_CUST, customer_login_db.user_name, EXPIRE_1_WEEK],
                ]
                redirect = _redirect(
                    destination="customer_OrderPlacement", cookies=cookies
                )
                return redirect, 302
            else:
                flash(INVALID_CRED)
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="customer_signin", cookies=cookies)
                return redirect, 302

        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                # Existing Cookie belongs to user in DB
                cookies = [
                    [AUTH_COOKIE_CUST, req_cookies[AUTH_COOKIE_CUST], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(
                    destination="customer_OrderPlacement", cookies=cookies
                )
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="customer_signin", cookies=cookies)
                return redirect, 302

    else:
        abort(401)


@app.route("/customer/editorder/<int:order_id>/<action>", methods=[GET])
def customer_editOrder(order_id: int, action: str):
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is not None:
            # Check Cookie
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                customer_orders_db = CustomerOrder.query.filter(
                    CustomerOrder.customer_id == customer_login_db.id,
                    CustomerOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )
                if customer_orders_db is not None and customer_orders_db.count() > 0:
                    customer_order = customer_orders_db.filter(
                        CustomerOrder.order_line_id == order_id,
                    ).first()
                    if customer_order is not None:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == customer_order.order_line_id,
                        ).first()
                        if order_line_db is not None:
                            product_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            if product_db is not None:
                                if action == "+":
                                    order_line_db.quant = order_line_db.quant + 1
                                    if (
                                        product_db.available_quant
                                        <= order_line_db.quant
                                    ):
                                        order_line_db.quant = order_line_db.quant - 1
                                        flash(f"Product : {product_db.name}")
                                        flash(f"Stock Insufficient")
                                    else:
                                        flash(f"Order Line Updated")
                                elif action == "-":
                                    if order_line_db.quant > 0:
                                        order_line_db.quant = order_line_db.quant - 1
                                        flash(f"Order Line Updated")
                                else:
                                    pass

                                if order_line_db.quant == 0:
                                    db.session.delete(order_line_db)
                                    flash("Order Line Deleted")

                                try:
                                    db.session.commit()
                                except sqlite3.OperationalError as e:
                                    print(f"Error : {str(e)}")
                                    sleep(1)
                                    db.session.commit()
                    cookies = [
                        [
                            AUTH_COOKIE_CUST,
                            req_cookies[AUTH_COOKIE_CUST],
                            EXPIRE_1_WEEK,
                        ],
                    ]
                    redirect = _redirect(
                        destination="customer_OrderPlacement", cookies=cookies
                    )
                    return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="customer_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="customer_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


class CustomerOrderAdd:
    def __init__(self, name: str, quantity: str):
        self.name = name.upper()
        self.quantity = int(quantity)


@app.route("/customer/addorder/", methods=[POST])
def customer_addOrder():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == POST:
        if req_cookies[AUTH_COOKIE_CUST] is not None:
            # Check Cookie
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                form_data = request.form
                customer_order_add_ref = CustomerOrderAdd(
                    name=form_data["name"],
                    quantity=form_data["quantity"],
                )
                product_db = Product.query.filter(
                    Product.name == customer_order_add_ref.name,
                ).first()
                if product_db is not None:
                    flag_prod_exists = False
                    customer_orders_db = CustomerOrder.query.filter(
                        CustomerOrder.customer_id == customer_login_db.id,
                        CustomerOrder.status == OrderStatus.ORDER_INCOMPLETE,
                    )
                    if customer_orders_db is not None:
                        for customer_order_db in customer_orders_db:
                            order_line_db = OrderLine.query.filter(
                                OrderLine.id == customer_order_db.order_line_id,
                                OrderLine.type == True,
                            ).first()
                            if order_line_db is not None:
                                if order_line_db.product_id == product_db.id:
                                    flag_prod_exists = True
                                    break

                    if flag_prod_exists:
                        flash(f"Product: [{product_db.id}] {product_db.name}")
                        flash("Product Exists in Cart")
                    else:
                        if product_db.available_quant < customer_order_add_ref.quantity:
                            flash(f"Product : {product_db.name}")
                            flash("Stock Insufficient")
                        else:
                            order_line_db = OrderLine(
                                quant=customer_order_add_ref.quantity,
                                price=product_db.price,
                                product_id=product_db.id,
                                type=True,
                            )
                            db.session.add(order_line_db)
                            try:
                                db.session.commit()
                            except sqlite3.OperationalError as e:
                                print(f"Error : {str(e)}")
                                sleep(1)
                                db.session.commit()
                            db.session.refresh(order_line_db)

                            customer_order_db = CustomerOrder(
                                status=OrderStatus.ORDER_INCOMPLETE,
                                order_line_id=order_line_db.id,
                                customer_id=customer_login_db.id,
                            )
                            db.session.add(customer_order_db)
                            try:
                                db.session.commit()
                            except sqlite3.OperationalError as e:
                                print(f"Error : {str(e)}")
                                sleep(1)
                                db.session.commit()

                            flash(f"Product : {product_db.name}")
                            flash(f"Added to Cart")
                    cookies = [
                        [
                            AUTH_COOKIE_CUST,
                            req_cookies[AUTH_COOKIE_CUST],
                            EXPIRE_1_WEEK,
                        ],
                    ]
                    redirect = _redirect(
                        destination="customer_OrderPlacement", cookies=cookies
                    )
                    return redirect, 302
                else:
                    flash(f"Product : {customer_order_add_ref.name}")
                    flash(f"Invalid Product Name")

                    products_db = Product.query.filter(
                        Product.name.like(f"%{customer_order_add_ref.name}%")
                    )
                    if products_db is not None and products_db.count() > 0:
                        flash("Possible Entries :")
                        for product in products_db:
                            flash(f"Product : {product.name}")
                    cookies = [
                        [
                            AUTH_COOKIE_CUST,
                            req_cookies[AUTH_COOKIE_CUST],
                            EXPIRE_1_WEEK,
                        ],
                    ]
                    redirect = _redirect(
                        destination="customer_OrderPlacement", cookies=cookies
                    )
                    return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(
                    destination="customer_OrderPlacement", cookies=cookies
                )
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="customer_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/customer/orderDel", methods=[GET])
def customer_orderDel():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is not None:
            # Check Cookie
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                customer_orders_db = CustomerOrder.query.filter(
                    CustomerOrder.customer_id == customer_login_db.id,
                    CustomerOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )

                if customer_orders_db is not None and customer_orders_db.count() > 0:
                    for customer_order in customer_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == customer_order.order_line_id
                        ).first()
                        db.session.delete(order_line_db)
                try:
                    db.session.commit()
                except sqlite3.OperationalError as e:
                    print(f"Error : {str(e)}")
                    sleep(1)
                    db.session.commit()
                flash(f"Order Lines Deleted")
                cookies = [
                    [AUTH_COOKIE_CUST, req_cookies[AUTH_COOKIE_CUST], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(
                    destination="customer_OrderPlacement", cookies=cookies
                )
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="customer_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="customer_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


class CustomerOrderPlacement:
    def __init__(self, deliveryChoice: str):
        self.deliveryChoice = deliveryChoice
        if self.deliveryChoice == BLANK:
            self.deliveryChoice = "PU"
        self.deliveryChoice = self.deliveryChoice.upper()


@app.route("/customer/orderplacement", methods=[GET, POST])
def customer_OrderPlacement():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is not None:
            # Check Cookie
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                customer_orders_db = CustomerOrder.query.filter(
                    CustomerOrder.customer_id == customer_login_db.id,
                    CustomerOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )

                order_lines = []
                if customer_orders_db is not None and customer_orders_db.count() > 0:
                    count = 0
                    for customer_order in customer_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == customer_order.order_line_id,
                            OrderLine.type == True,
                        ).first()
                        if order_line_db is not None:
                            count = count + 1
                            product_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            order_lines.append(
                                {
                                    "sl_no": count,
                                    "order_id": order_line_db.id,
                                    "name": product_db.name
                                    if product_db is not None
                                    else None,
                                    "price": order_line_db.price,
                                    "quantity": order_line_db.quant,
                                    "subtotal": order_line_db.price
                                    * order_line_db.quant,
                                }
                            )

                page_name = "customer_OrderPlacement.html"
                path = os.path.join(page_name)
                return render_template(path, data=order_lines)
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="customer_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="customer_signin", cookies=cookies)
            return redirect, 302

    elif req_method == POST:
        if req_cookies[AUTH_COOKIE_CUST] is not None:
            # Check Cookie
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                form_data = request.form
                customer_order_ref = CustomerOrderPlacement(
                    deliveryChoice=form_data["deliveryChoice"]
                )
                customer_orders_db = CustomerOrder.query.filter(
                    CustomerOrder.customer_id == customer_login_db.id,
                    CustomerOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )
                if customer_orders_db is not None and customer_orders_db.count() > 0:
                    price = 0
                    order_content_str = []
                    for customer_order in customer_orders_db:
                        customer_order.delivery = customer_order_ref.deliveryChoice

                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == customer_order.order_line_id,
                            OrderLine.type == True,
                        ).first()
                        if order_line_db is not None:
                            price = price + (order_line_db.quant * order_line_db.price)
                            product_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            if product_db is not None:
                                if len(order_content_str) <= 0:
                                    order_content_str.append(
                                        "{}\t\t{}\t\t{}\t\t{}".format(
                                            "Product Name",
                                            "Quantity",
                                            "Price per Unit",
                                            "Subtotal",
                                        )
                                    )
                                order_content_str.append(
                                    "{}\t\t\t{}\t\t\t{}\t\t\t{}".format(
                                        product_db.name,
                                        order_line_db.quant,
                                        order_line_db.price,
                                        order_line_db.quant * order_line_db.price,
                                    )
                                )
                    order_head_db = OrderHead(
                        price=price,
                    )
                    db.session.add(order_head_db)
                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()
                    db.session.refresh(order_head_db)

                    for customer_order in customer_orders_db:
                        customer_order.status = OrderStatus.ORDER_COMPLETE
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == customer_order.order_line_id,
                            OrderLine.type == True,
                        ).first()
                        if order_line_db is not None:
                            order_line_db.order_head_id = order_head_db.id

                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()

                    cust_details_db = CustomerDetails.query.filter(
                        CustomerDetails.customer_login_id == customer_login_db.id,
                    ).first()
                    if cust_details_db is not None:
                        body = f"""
                            Hi {cust_details_db.first_name},

                            You have placed an Online Order.
                            For : {"Home Delivery" if customer_order_ref.deliveryChoice == "HD" else "In Store Pick Up"}

                            Order ID : {order_head_db.id}

                            Order Contents are
                            """
                        for order in order_content_str:
                            body = (
                                body
                                + f"""
                                {order}
                                """
                            )
                        body = (
                            body
                            + f"""
                            Total : {order_head_db.price}

                            Thanks and Regards,
                            Bot.
                            """
                        )
                        email_send_ref = EmailSend(
                            thread_name="Customer Order Creation",
                            email=cust_details_db.emailID,
                            subject=f"{server_name} | Customer | Order Created | {order_head_db.id}",
                            body=body,
                        )
                        email_send_ref.start()
                    flash(f"Order Id : {order_head_db.id}")
                    flash(f"Order Created")
                cookies = [
                    [AUTH_COOKIE_CUST, req_cookies[AUTH_COOKIE_CUST], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(
                    destination="customer_OrderPlacement", cookies=cookies
                )
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="customer_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="customer_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


class CustomerSignup:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        address: str,
        password: str,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.password = password
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password.encode("utf-8"))
        self.password = password_hash.hexdigest()[:254]


@app.route("/customer/signup", methods=[GET, POST])
def customer_SignUp():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user logged in
            page_name = "customer_signup.html"
            path = os.path.join(page_name)
            return render_template(path)
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                # Existing Cookie belongs to user in DB
                cookies = [
                    [AUTH_COOKIE_CUST, req_cookies[AUTH_COOKIE_CUST], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(
                    destination="customer_OrderPlacement", cookies=cookies
                )
                return redirect, 302
            else:
                page_name = "customer_signup.html"
                path = os.path.join(page_name)
                return render_template(path)

    elif req_method == POST:
        form_data = request.form
        customer_signup_ref = CustomerSignup(
            first_name=form_data["firstName"],
            last_name=form_data["lastName"],
            email=form_data["email"],
            phone=form_data["mobile"],
            address=form_data["address"],
            password=form_data["psw"],
        )

        # Creating Database Entry for New Customer Data >>>>>>>>>>

        # Check if same email <> username exists or not
        customer_login_db = CustomerLogin.query.filter(
            CustomerLogin.user_name == customer_signup_ref.email.upper()
        ).first()
        if customer_login_db is not None:
            # If user exists -> Redirect to Signup Page
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            flash("Email ID Exists")
            redirect = _redirect(destination="customer_SignUp", cookies=cookies)
            return redirect, 302
        else:
            # User does not exists -> Create New user
            del customer_login_db

            customer_login_db = CustomerLogin(
                user_name=customer_signup_ref.email.upper(),
                password_hash=customer_signup_ref.password,
            )
            customer_details_db = CustomerDetails(
                first_name=customer_signup_ref.first_name.upper(),
                last_name=customer_signup_ref.last_name.upper(),
                emailID=customer_signup_ref.email,
                phoneNumber=customer_signup_ref.phone,
                address=customer_signup_ref.address,
            )

            db.session.add(customer_login_db)
            try:
                db.session.commit()
            except sqlite3.OperationalError as e:
                print(f"Error : {str(e)}")
                sleep(1)
                db.session.commit()
            db.session.refresh(customer_login_db)
            customer_details_db.customer_login_id = customer_login_db.id
            db.session.add(customer_details_db)
            try:
                db.session.commit()
            except sqlite3.OperationalError as e:
                print(f"Error : {str(e)}")
                sleep(1)
                db.session.commit()

            email_send_ref = EmailSend(
                thread_name="Customer Signup",
                email=customer_signup_ref.email,
                subject=f"{server_name} | Customer Account Created",
                body=f"""
                Hi {customer_signup_ref.first_name},
                
                Welcome to {server_name}
                
                User ID : {customer_signup_ref.email}
                Password : {form_data["psw"]}
                
                Thanks and Regards,
                Bot.
                """,
            )
            email_send_ref.start()

            # If New user -> Redirect to Order Placement Page
            cookies = [
                [AUTH_COOKIE_CUST, customer_login_db.user_name, EXPIRE_1_WEEK],
            ]
            redirect = _redirect(destination="customer_OrderPlacement", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


class CustomerEditProfile:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        mobile: str,
        address: str,
        psw_old: str,
        psw: str,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.mobile = mobile
        self.address = address
        self.password_old = psw_old
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password_old.encode("utf-8"))
        self.password_old = password_hash.hexdigest()[:254]
        self.password_new = psw
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password_new.encode("utf-8"))
        self.password_new = password_hash.hexdigest()[:254]


@app.route("/customer/editprofile", methods=[GET, POST])
def customer_editProfile():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user logged in
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="customer_signin", cookies=cookies)
            return redirect, 302
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                flag_user_exists = True
            else:
                flag_user_exists = False

            if flag_user_exists:
                customer_details_db = CustomerDetails.query.filter(
                    CustomerDetails.customer_login_id == customer_login_db.id,
                ).first()
                if customer_details_db is not None:
                    # Existing Cookie belongs to user in DB
                    data = {
                        "first_name": customer_details_db.first_name,
                        "last_name": customer_details_db.last_name,
                        "email": customer_details_db.emailID,
                        "mobile": customer_details_db.phoneNumber,
                        "address": customer_details_db.address,
                    }
                else:
                    data = {
                        "first_name": "Dummy Data",
                        "last_name": "Dummy Data",
                        "email": "Dummy Data",
                        "mobile": "Dummy Data",
                        "address": "Dummy Data",
                    }
                page_name = "customer_editProfile.html"
                path = os.path.join(page_name)
                return render_template(path, data=data)
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="customer_signin", cookies=cookies)
                return redirect, 302

    elif req_method == POST:
        form_data = request.form
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user logged in
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="customer_signin", cookies=cookies)
            return redirect, 302
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                flag_user_exists = True
            else:
                flag_user_exists = False

            if flag_user_exists:
                # Existing Cookie belongs to user in DB
                customer_edit_profile_ref = CustomerEditProfile(
                    first_name=form_data["firstName"],
                    last_name=form_data["lastName"],
                    email=form_data["email"],
                    mobile=form_data["mobile"],
                    address=form_data["address"],
                    psw_old=form_data["psw_old"],
                    psw=form_data["psw"],
                )

                customer_login_db = CustomerLogin.query.filter(
                    CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
                ).first()
                if customer_login_db is not None:
                    # Check if email has been changed
                    if (
                        customer_login_db.user_name
                        != customer_edit_profile_ref.email.upper()
                    ):
                        # Check if someone else has the same email id
                        customer_login_db_other = CustomerLogin.query.filter(
                            CustomerLogin.user_name
                            == customer_edit_profile_ref.email.upper(),
                        ).first()
                        if customer_login_db_other is not None:
                            # Redirect to self using a message
                            if customer_login_db.id != customer_login_db_other.id:
                                flash("Email ID Exists")
                                cookies = [
                                    [
                                        AUTH_COOKIE_CUST,
                                        req_cookies[AUTH_COOKIE_CUST],
                                        EXPIRE_1_WEEK,
                                    ],
                                ]
                                redirect = _redirect(
                                    destination="customer_editProfile", cookies=cookies
                                )
                                return redirect, 302
                            else:
                                customer_login_db.user_name = (
                                    customer_edit_profile_ref.email.upper()
                                )

                    # Check if old and existing password matches
                    if (
                        customer_edit_profile_ref.password_old
                        != customer_login_db.password_hash
                    ):
                        # Redirect to self using a message
                        flash("Existing Password is wrong")
                        cookies = [
                            [
                                AUTH_COOKIE_CUST,
                                req_cookies[AUTH_COOKIE_CUST],
                                EXPIRE_1_WEEK,
                            ],
                        ]
                        redirect = _redirect(
                            destination="customer_editProfile", cookies=cookies
                        )
                        return redirect, 302
                    else:
                        # Check if old password and new passwords are different
                        if (
                            customer_edit_profile_ref.password_old
                            != customer_edit_profile_ref.password_new
                        ):
                            customer_login_db.password_hash = (
                                customer_edit_profile_ref.password_new
                            )

                    # Get related Customer Details Entry
                    customer_details_db = CustomerDetails.query.filter(
                        CustomerDetails.customer_login_id == customer_login_db.id,
                    ).first()
                    if customer_details_db is not None:
                        customer_details_db.first_name = (
                            customer_edit_profile_ref.first_name
                        )
                        customer_details_db.last_name = (
                            customer_edit_profile_ref.last_name
                        )
                        customer_details_db.emailID = customer_edit_profile_ref.email
                        customer_details_db.phoneNumber = (
                            customer_edit_profile_ref.mobile
                        )
                        customer_details_db.address = customer_edit_profile_ref.address

                        # Commit all changes
                        try:
                            db.session.commit()
                        except sqlite3.OperationalError as e:
                            print(f"Error : {str(e)}")
                            sleep(1)
                            db.session.commit()

                        # Redirect to self using a message
                        flash("Update Successful")
                        cookies = [
                            [
                                AUTH_COOKIE_CUST,
                                req_cookies[AUTH_COOKIE_CUST],
                                EXPIRE_1_WEEK,
                            ],
                        ]
                        redirect = _redirect(
                            destination="customer_editProfile", cookies=cookies
                        )
                        return redirect, 302

            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="customer_signin", cookies=cookies)
                return redirect, 302
    else:
        abort(401)


@app.route("/customer/logout", methods=[GET])
def customerLogout():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        cookies = [
            [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
        ]
        redirect = _redirect(destination="customer_signin", cookies=cookies)
        return redirect, 302
    else:
        abort(401)


class CustomerForgotPassword:
    def __init__(self, email):
        self.email = email


@app.route("/customer/forget_password", methods=[GET, POST])
def customerForgotPWD():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        page_name = "customer_forgotPwd.html"
        path = os.path.join(page_name)
        return render_template(path)
    elif req_method == POST:
        form_data = request.form
        customer_forgot_password_ref = CustomerForgotPassword(email=form_data["email"])
        # Check if email exists
        customer_login_db = CustomerLogin.query.filter(
            CustomerLogin.user_name == customer_forgot_password_ref.email.upper(),
        ).first()
        if customer_login_db is not None:
            # Email in Database
            char_list = f"{string.ascii_letters}{string.digits}{string.punctuation}"
            new_password = []
            for i in range(16):
                new_password.append(random.choice(char_list))
            new_password = "".join(new_password)
            # Hash actual password
            password_hash = hashlib.sha1()
            password_hash.update(new_password.encode("utf-8"))
            customer_login_db.password_hash = password_hash.hexdigest()[:254]
            try:
                db.session.commit()
            except sqlite3.OperationalError as e:
                print(f"Error : {str(e)}")
                sleep(1)
                db.session.commit()
            email_send_ref = EmailSend(
                thread_name="Forgot Password",
                email=customer_forgot_password_ref.email,
                subject=f"{server_name} | Reset Password",
                body=f"Your new password is : {new_password}",
            )
            email_send_ref.start()
            flash("New Password sent to Email id")
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="customerForgotPWD", cookies=cookies)
            return redirect, 302
        else:
            # Email not in Database
            flash("Email does not exist")
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="customerForgotPWD", cookies=cookies)
            return redirect, 302


# ======================
# Routing Employee


class EmployeeSignin:
    def __init__(self, login_id: str, password: str):
        self.login_id = login_id.upper()
        self.password = password
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password.encode("utf-8"))
        self.password = password_hash.hexdigest()[:254]


@app.route("/employee", methods=[GET, POST])
def employee_signin():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is None:
            # No user logged in
            page_name = "employee_signin.html"
            path = os.path.join(page_name)
            return render_template(path)
        else:
            # User already logged in
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                # Existing Cookie belongs to user in DB
                cookies = [
                    [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="employeeWelcome", cookies=cookies)
                return redirect, 302
            else:
                page_name = "employee_signin.html"
                path = os.path.join(page_name)
                return render_template(path)

    elif req_method == POST:
        if req_cookies[AUTH_COOKIE_EMP] is None:
            # No user logged in
            form_data = request.form
            employee_signin_ref = EmployeeSignin(
                login_id=form_data["loginID"],
                password=form_data["password"],
            )
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == employee_signin_ref.login_id.upper(),
                EmployeeLogin.password_hash == employee_signin_ref.password,
            ).first()
            if employee_login_db is not None:
                # Correct Credentials
                cookies = [
                    [AUTH_COOKIE_EMP, employee_login_db.user_name, EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="employeeWelcome", cookies=cookies)
                return redirect, 302
            else:
                # Wrong Credentials
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                flash(INVALID_CRED)
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                # Existing Cookie belongs to user in DB
                cookies = [
                    [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="employeeWelcome", cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                flash("Enter Credentials again !")
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302

    else:
        abort(401)


@app.route("/employee/welcome", methods=[GET, POST])
def employeeWelcome():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                page_name = "employee_welcome.html"
                path = os.path.join(page_name)
                return render_template(path)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302
    else:
        abort(401)


class EmployeeInventory:
    def __init__(
        self,
        name: str,
        price: str,
        shelf: str,
        quant_a: str,
        returns: str,
        quant_r: str,
    ):
        self.name = name.upper()
        self.price = float(price)
        self.quant_a = int(quant_a)
        self.quant_r = int(quant_r)
        self.returns = True if returns.upper() == "YES" else False
        self.shelf = shelf.upper()


@app.route("/employee/inventory", methods=[GET, POST])
def employeeInventory():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                products_db = Product.query.all()
                data = []
                for product in products_db:
                    data.append(
                        {
                            "id": product.id,
                            "name": product.name,
                            "price": product.price,
                            "quant_a": product.available_quant,
                            "shelf": product.shelf_loc,
                            "returns": "Yes" if product.accp_return is True else "No",
                            "quant_r": product.reorder_quant,
                        }
                    )
                page_name = "employee_inventory.html"
                path = os.path.join(page_name)
                return render_template(path, data=data)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    elif req_method == POST:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Cookie Present
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                # Cookie is okay
                form_data = request.form
                employee_inventory_ref = EmployeeInventory(
                    name=form_data["productName"],
                    price=form_data["productPrice"],
                    quant_a=form_data["quantityAvailable"],
                    quant_r=form_data["reorderQty"],
                    returns=form_data["acceptReturns"],
                    shelf=form_data["shelfLocation"],
                )
                product_db = Product.query.filter(
                    Product.name == employee_inventory_ref.name,
                ).first()
                if product_db is not None:
                    # Product exists
                    flash(f"Product : [{product_db.id}] {product_db.name}")
                    flash(f"Product Exists")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(
                        destination="employeeInventory", cookies=cookies
                    )
                    return redirect, 302
                else:
                    # Create Product
                    product_db = Product(
                        name=employee_inventory_ref.name,
                        available_quant=employee_inventory_ref.quant_a,
                        reorder_quant=employee_inventory_ref.quant_r,
                        price=employee_inventory_ref.price,
                        shelf_loc=employee_inventory_ref.shelf,
                        accp_return=employee_inventory_ref.returns,
                    )
                    db.session.add(product_db)
                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()
                    db.session.refresh(product_db)

                    flash(f"Product : [{product_db.id}] {product_db.name}")
                    flash("Product Added")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(
                        destination="employeeInventory", cookies=cookies
                    )
                    return redirect, 302
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/inventoryprint", methods=[GET])
def employeeInventoryPrint():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                products_db = Product.query.all()
                data = []
                for product in products_db:
                    data.append(
                        {
                            "id": product.id,
                            "name": product.name,
                            "price": product.price,
                            "quant_a": product.available_quant,
                            "shelf": product.shelf_loc,
                            "returns": "Yes" if product.accp_return is True else "No",
                            "quant_r": product.reorder_quant,
                        }
                    )
                page_name = "employee_inventory_print.html"
                path = os.path.join(page_name)
                html_code = render_template(path, data=data)
                page_name = "{}_{}.htm".format(
                    page_name.split(".")[0], random.choice([x for x in range(1, 1000)])
                )
                file_path = os.path.join(PROJECT_DIR, "temp_files", page_name)
                # return Response(
                #     html_code,
                #     mimetype="text/html",
                #     headers={
                #         "Content-disposition": "attachment; filename={}".format(
                #             page_name
                #         )
                #     },
                # )
                try:
                    pdfkit.from_string(
                        html_code, file_path, options={"enable-local-file-access": ""}
                    )
                except Exception as e:
                    print("PDF generaion error : ", str(e))
                    page_name = "employee_inventory.html"
                    path = os.path.join(page_name)
                    return render_template(path, data=data)
                else:
                    pdf_bin = None
                    with open(file_path, "rb") as pdf_file:
                        pdf_bin = pdf_file.read()
                    if pdf_bin is not None:
                        return Response(
                            pdf_bin,
                            mimetype="application/pdf",
                            headers={
                                "Content-disposition": "attachment; filename=inventory.pdf"
                            },
                        )
                    else:
                        page_name = "employee_inventory.html"
                        path = os.path.join(page_name)
                        return render_template(path, data=data)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/editItemInfo/<int:prod_id>", methods=[GET, POST])
def employeeEditItemInfo(prod_id: int):
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                product_db = Product.query.filter(
                    Product.id == prod_id,
                ).first()
                if product_db is not None:
                    data = {
                        "id": product_db.id,
                        "name": product_db.name,
                        "price": product_db.price,
                        "quant_a": product_db.available_quant,
                        "shelf": product_db.shelf_loc,
                        "returns": "Yes" if product_db.accp_return is True else "No",
                        "quant_r": product_db.reorder_quant,
                    }
                    page_name = "employee_inventoryEdit.html"
                    path = os.path.join(page_name)
                    return render_template(path, data=data)
                else:
                    flash(f"Product Id : {prod_id}")
                    flash(f"Invalid Id")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(
                        destination="employeeInventory", cookies=cookies
                    )
                    return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    elif req_method == POST:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Cookie Present
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                # Cookie is okay
                product_db = Product.query.filter(
                    Product.id == prod_id,
                ).first()
                if product_db is not None:
                    form_data = request.form
                    employee_inventory_ref = EmployeeInventory(
                        name=form_data["itemName"],
                        price=form_data["price"],
                        quant_a=form_data["qtyAvailable"],
                        quant_r=form_data["reorderQty"],
                        returns=form_data["acceptReturns"],
                        shelf=form_data["shelfLocation"],
                    )

                    product_db.name = employee_inventory_ref.name
                    product_db.available_quant = employee_inventory_ref.quant_a
                    product_db.price = employee_inventory_ref.price
                    product_db.shelf_loc = employee_inventory_ref.shelf
                    product_db.accp_return = employee_inventory_ref.returns
                    product_db.reorder_quant = employee_inventory_ref.quant_r
                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()

                    flash(f"Product : [{product_db.id}] {product_db.name}")
                    flash(f"Info Updated")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(
                        destination="employeeInventory", cookies=cookies
                    )
                    return redirect, 302
                else:
                    flash(f"Product Id : {prod_id}")
                    flash("Invalid ID")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(
                        destination="employeeInventory", cookies=cookies
                    )
                    return redirect, 302
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/delItemInfo/<int:prod_id>", methods=[GET])
def employeeDelItemInfo(prod_id: int):
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                product_db = Product.query.filter(
                    Product.id == prod_id,
                ).first()
                prod_name = None
                if product_db is not None:
                    prod_name = product_db.name
                    db.session.delete(product_db)
                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()

                    flash(f"Product : [{prod_id}] {prod_name}")
                    flash("Product Deleted")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(
                        destination="employeeInventory", cookies=cookies
                    )
                    return redirect, 302
                else:
                    flash(f"Product Id : {prod_id}")
                    flash(f"Invalid ID")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(
                        destination="employeeInventory", cookies=cookies
                    )
                    return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


class EmployeePosTerminalAdd:
    def __init__(self, quantity: int, prod_id: int):
        self.quantity = quantity
        self.prod_id = prod_id


@app.route("/employee/posTerminalAdd/", methods=[POST])
def employeePosTerminalAdd():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == POST:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                form_data = request.form
                employee_pos_terminal_add_ref = EmployeePosTerminalAdd(
                    prod_id=int(form_data["productID"]),
                    quantity=1,
                )
                product_db = Product.query.filter(
                    Product.id == employee_pos_terminal_add_ref.prod_id,
                ).first()
                if product_db is not None:
                    employee_orders_db = EmployeeOrder.query.filter(
                        EmployeeOrder.employee_id == employee_login_db.id,
                        EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                    )
                    flag_prod_exists = False
                    if employee_orders_db is not None:
                        for employee_order_db in employee_orders_db:
                            order_line_db = OrderLine.query.filter(
                                OrderLine.id == employee_order_db.order_line_id,
                                OrderLine.type == True,
                            ).first()
                            if order_line_db is not None:
                                if order_line_db.product_id == product_db.id:
                                    flag_prod_exists = True
                            if flag_prod_exists:
                                break
                    if flag_prod_exists:
                        flash(f"Product : [{product_db.id}] {product_db.name}")
                        flash(f"Exists in Cart")
                    else:
                        if product_db.available_quant > 0:
                            order_line_db = OrderLine(
                                quant=employee_pos_terminal_add_ref.quantity,
                                price=product_db.price,
                                product_id=employee_pos_terminal_add_ref.prod_id,
                                type=True,
                            )
                            if (
                                product_db.available_quant
                                < product_db.reorder_quant / 2
                            ):
                                flash(f"Product: {product_db.name}")
                                flash(f"Stock Left: {product_db.available_quant - 1}")
                            db.session.add(order_line_db)
                            product_db.available_quant = (
                                product_db.available_quant
                                - employee_pos_terminal_add_ref.quantity
                            )
                        else:
                            flash(f"Product: {product_db.name}")
                            flash(f"Stock Left: {product_db.available_quant}")
                        try:
                            db.session.commit()
                        except sqlite3.OperationalError as e:
                            print(f"Error : {str(e)}")
                            sleep(1)
                            db.session.commit()
                        db.session.refresh(order_line_db)

                        employee_order_db = EmployeeOrder(
                            status=OrderStatus.ORDER_INCOMPLETE,
                            order_line_id=order_line_db.id,
                            employee_id=employee_login_db.id,
                        )
                        db.session.add(employee_order_db)
                        try:
                            db.session.commit()
                        except sqlite3.OperationalError as e:
                            print(f"Error : {str(e)}")
                            sleep(1)
                            db.session.commit()

                        flash(f"Product : [{product_db.id}] {product_db.name}")
                        flash(f"Added To Cart")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(
                        destination="employeePosTerminal", cookies=cookies
                    )
                    return redirect, 302
                else:
                    flash(f"Product Id : {employee_pos_terminal_add_ref.prod_id}")
                    flash("Invalid ID")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(
                        destination="employeePosTerminal", cookies=cookies
                    )
                    return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employeePosTerminal", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/posTerminalEdit/<int:order_id>/<action>", methods=[GET])
def employeePosTerminalEdit(order_id: int, action: str):
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                employee_orders_db = EmployeeOrder.query.filter(
                    EmployeeOrder.employee_id == employee_login_db.id,
                    EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )
                if employee_orders_db is not None and employee_orders_db.count() > 0:
                    employee_order = employee_orders_db.filter(
                        EmployeeOrder.order_line_id == order_id,
                    ).first()
                    if employee_order is not None:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == employee_order.order_line_id,
                        ).first()
                        if order_line_db is not None:
                            product_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            if product_db is not None:
                                if action == "+":
                                    if product_db.available_quant > 0:
                                        order_line_db.quant = order_line_db.quant + 1
                                        product_db.available_quant = (
                                            product_db.available_quant - 1
                                        )
                                        if product_db.available_quant < (
                                            product_db.reorder_quant / 2
                                        ):
                                            flash(
                                                f"Product : [{product_db.id}] {product_db.name}"
                                            )
                                            flash(
                                                f"Quantity left : {product_db.available_quant}"
                                            )
                                        else:
                                            flash(f"Order Line Updated")
                                elif action == "-":
                                    if order_line_db.quant > 0:
                                        order_line_db.quant = order_line_db.quant - 1
                                        product_db.available_quant = (
                                            product_db.available_quant + 1
                                        )
                                        flash(f"Order Line Updated")
                                else:
                                    pass

                                if order_line_db.quant == 0:
                                    db.session.delete(order_line_db)
                                    flash(f"Order Line Deleted")

                                try:
                                    db.session.commit()
                                except sqlite3.OperationalError as e:
                                    print(f"Error : {str(e)}")
                                    sleep(1)
                                    db.session.commit()
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(
                        destination="employeePosTerminal", cookies=cookies
                    )
                    return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employeePosTerminal", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/posTerminalDel/<int:order_id>", methods=[GET])
def employeePosTerminalDel(order_id: int):
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                employee_orders_db = EmployeeOrder.query.filter(
                    EmployeeOrder.employee_id == employee_login_db.id,
                    EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )

                if order_id == 0:  # Delete All
                    if (
                        employee_orders_db is not None
                        and employee_orders_db.count() > 0
                    ):
                        for employee_order in employee_orders_db:
                            order_line_db = OrderLine.query.filter(
                                OrderLine.id == employee_order.order_line_id
                            ).first()
                            if order_line_db is not None:
                                product_db = Product.query.filter(
                                    Product.id == order_line_db.product_id
                                ).first()
                                if product_db is not None:
                                    product_db.available_quant = (
                                        product_db.available_quant + order_line_db.quant
                                    )
                                db.session.delete(order_line_db)
                else:
                    if (
                        employee_orders_db is not None
                        and employee_orders_db.count() > 0
                    ):
                        employee_order = employee_orders_db.filter(
                            EmployeeOrder.order_line_id == order_id,
                        ).first()
                        if employee_order is not None:
                            order_line_db = OrderLine.query.filter(
                                OrderLine.id == employee_order.order_line_id,
                            ).first()
                            if order_line_db is not None:
                                product_db = Product.query.filter(
                                    Product.id == order_line_db.product_id
                                ).first()
                                if product_db is not None:
                                    product_db.available_quant = (
                                        product_db.available_quant + order_line_db.quant
                                    )
                                db.session.delete(order_line_db)
                try:
                    db.session.commit()
                except sqlite3.OperationalError as e:
                    print(f"Error : {str(e)}")
                    sleep(1)
                    db.session.commit()
                flash(f"Order Line{'s' if order_id == 0 else BLANK} Deleted")
                cookies = [
                    [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="employeePosTerminal", cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/posTerminal/", methods=[GET, POST])
def employeePosTerminal():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                employee_orders_db = EmployeeOrder.query.filter(
                    EmployeeOrder.employee_id == employee_login_db.id,
                    EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )

                order_lines = []
                if employee_orders_db is not None and employee_orders_db.count() > 0:
                    count = 0
                    for employee_order in employee_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == employee_order.order_line_id,
                            OrderLine.type == True,
                        ).first()
                        if order_line_db is not None:
                            count = count + 1
                            product_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            order_lines.append(
                                {
                                    "id": product_db.id
                                    if product_db is not None
                                    else None,
                                    "name": product_db.name
                                    if product_db is not None
                                    else None,
                                    "price": order_line_db.price,
                                    "quantity": order_line_db.quant,
                                    "sl_no": count,
                                    "order_id": order_line_db.id,
                                    "subtotal": order_line_db.price
                                    * order_line_db.quant,
                                }
                            )

                page_name = "employee_posTerminal.html"
                path = os.path.join(page_name)
                return render_template(path, data=order_lines)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    elif req_method == POST:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                employee_orders_db = EmployeeOrder.query.filter(
                    EmployeeOrder.employee_id == employee_login_db.id,
                    EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )
                if employee_orders_db is not None and employee_orders_db.count() > 0:
                    price = 0
                    order_content_str = []
                    for employee_order in employee_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == employee_order.order_line_id,
                            OrderLine.type == True,
                        ).first()
                        if order_line_db is not None:
                            price = price + (order_line_db.quant * order_line_db.price)
                            product_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            if product_db is not None:
                                if len(order_content_str) <= 0:
                                    order_content_str.append(
                                        "{}\t\t{}\t\t{}\t\t{}".format(
                                            "Product Name",
                                            "Quantity",
                                            "Price per Unit",
                                            "Subtotal",
                                        )
                                    )
                                order_content_str.append(
                                    "{}\t\t\t{}\t\t\t{}\t\t\t{}".format(
                                        product_db.name,
                                        order_line_db.quant,
                                        order_line_db.price,
                                        order_line_db.quant * order_line_db.price,
                                    )
                                )
                    order_head_db = OrderHead(
                        price=price,
                    )
                    db.session.add(order_head_db)
                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()
                    db.session.refresh(order_head_db)

                    for employee_order in employee_orders_db:
                        employee_order.status = OrderStatus.COMPLETE
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == employee_order.order_line_id,
                            OrderLine.type == True,
                        ).first()
                        if order_line_db is not None:
                            order_line_db.order_head_id = order_head_db.id

                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()

                    emp_details_db = EmployeeDetails.query.filter(
                        EmployeeDetails.employee_login_id == employee_login_db.id,
                    ).first()
                    if emp_details_db is not None:
                        body = f"""
                        Hi {emp_details_db.first_name},
                            
                        You have placed an Order from POS.
                            
                        Order ID : {order_head_db.id}
                            
                        Order Contents are
                        """
                        for order in order_content_str:
                            body = (
                                body
                                + f"""
                        {order}\n"""
                            )
                        body = (
                            body
                            + f"""
                        Total : {order_head_db.price}
                            
                        Thanks and Regards,
                        Bot.
                        """
                        )
                        email_send_ref = EmailSend(
                            thread_name="Employee Order Creation",
                            email=emp_details_db.emailID,
                            subject=f"{server_name} | Employee | Order Created | {order_head_db.id}",
                            body=body,
                        )
                        email_send_ref.start()

                    flash(f"Order ID : {order_head_db.id}")
                    flash(f"Order Created")
                cookies = [
                    [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="employeePosTerminal", cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employeePosTerminal", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/monthlyRevenue", methods=[GET])
def employeeMonthlyRevenue():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                orders = []
                data_raw = {}

                # Customer Orders => Accepted
                customer_orders_db = CustomerOrder.query.filter(
                    CustomerOrder.status == OrderStatus.ORDER_ACCEPTED
                )
                if customer_orders_db is not None:
                    for customer_order_db in customer_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == customer_order_db.order_line_id,
                        ).first()
                        if order_line_db is not None:
                            order_head_db = OrderHead.query.filter(
                                OrderHead.id == order_line_db.order_head_id,
                            ).first()
                            if order_head_db is not None:
                                if order_head_db.id not in orders:
                                    period = f"{order_head_db.created_at.year}{order_head_db.created_at.month if len(str(order_head_db.created_at.month)) == 2 else f'0{order_head_db.created_at.month}'}"
                                    orders.append(order_head_db.id)
                                    try:
                                        data_raw[period][0] = data_raw[period][0] + 1
                                        data_raw[period][1] = (
                                            data_raw[period][1] + order_head_db.price
                                        )
                                    except KeyError:
                                        data_raw.update(
                                            {
                                                period: [
                                                    1,
                                                    order_head_db.price,
                                                ]
                                            }
                                        )

                # Employee Orders => Completed ( Normal + Return )
                employee_orders_db = EmployeeOrder.query.filter(
                    EmployeeOrder.status == OrderStatus.COMPLETE
                )
                if employee_orders_db is not None:
                    for employee_order_db in employee_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == employee_order_db.order_line_id,
                        ).first()
                        if order_line_db is not None:
                            order_head_db = OrderHead.query.filter(
                                OrderHead.id == order_line_db.order_head_id,
                            ).first()
                            if order_head_db is not None:
                                if order_head_db.id not in orders:
                                    period = f"{order_head_db.created_at.year}{order_head_db.created_at.month if len(str(order_head_db.created_at.month)) == 2 else f'0{order_head_db.created_at.month}'}"
                                    orders.append(order_head_db.id)

                                    if order_line_db.type is True:  # Normal
                                        revenue = order_head_db.price
                                    else:
                                        revenue = order_head_db.price * -1

                                    try:
                                        data_raw[period][0] = data_raw[period][0] + 1
                                        data_raw[period][1] = (
                                            data_raw[period][1] + revenue
                                        )
                                    except KeyError:
                                        data_raw.update(
                                            {
                                                period: [
                                                    1,
                                                    revenue,
                                                ]
                                            }
                                        )

                data_revenue = []
                for key in sorted(data_raw.keys(), reverse=True):
                    period = f"{calendar.month_name[int(key[5:])]}/{key[0:4]}"
                    data_revenue.append(
                        {
                            "period": period,
                            "orders": data_raw[key][0],
                            "revenue": data_raw[key][1],
                        }
                    )

                page_name = "employee_monthlyRevenue.html"
                path = os.path.join(page_name)
                return render_template(path, data=data_revenue)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/orders", methods=[GET])
def employeeOrders():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                data = {
                    "table_1": [],
                    "table_2": [],
                }
                orders = []

                # Open Orders
                customer_orders_db = CustomerOrder.query.filter(
                    CustomerOrder.status == OrderStatus.ORDER_COMPLETE
                )
                if customer_orders_db is not None:
                    for customer_order in customer_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == customer_order.order_line_id,
                        ).first()
                        customer_details_db = CustomerDetails.query.filter(
                            CustomerDetails.customer_login_id
                            == customer_order.customer_id,
                        ).first()
                        if order_line_db is not None:
                            order_head_db = OrderHead.query.filter(
                                OrderHead.id == order_line_db.order_head_id,
                            ).first()
                            if (
                                order_head_db is not None
                                and order_head_db.id not in orders
                            ):
                                orders.append(order_head_db.id)
                                data["table_1"].append(
                                    {
                                        "order_id": order_head_db.id,
                                        "date": f"{order_head_db.created_at.date()}",
                                        "name": f"{customer_details_db.first_name} {customer_details_db.last_name}",
                                        "price": f"{order_head_db.price}",
                                        "delivery": f"""{
                                        'Home Delivery' if customer_order.delivery == 'HD' else 'In Store Pickup'
                                        }""",
                                    }
                                )

                # Closed Orders
                customer_orders_db = CustomerOrder.query.filter(
                    (CustomerOrder.status == OrderStatus.COMPLETE)
                    | (CustomerOrder.status == OrderStatus.ORDER_ACCEPTED)
                    | (CustomerOrder.status == OrderStatus.ORDER_REJECTED)
                )
                if customer_orders_db is not None:
                    for customer_order in customer_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == customer_order.order_line_id,
                        ).first()
                        customer_details_db = CustomerDetails.query.filter(
                            CustomerDetails.customer_login_id
                            == customer_order.customer_id,
                        ).first()
                        if order_line_db is not None:
                            order_head_db = OrderHead.query.filter(
                                OrderHead.id == order_line_db.order_head_id,
                            ).first()
                            if (
                                order_head_db is not None
                                and order_head_db.id not in orders
                            ):
                                orders.append(order_head_db.id)
                                data["table_2"].append(
                                    {
                                        "order_id": order_head_db.id,
                                        "date": f"{order_head_db.created_at.date()}",
                                        "name": f"{customer_details_db.first_name} {customer_details_db.last_name}",
                                        "price": f"{order_head_db.price}",
                                        "type1": "External",
                                        "type2": f"{customer_order.status}",
                                    }
                                )

                employee_orders_db = EmployeeOrder.query.filter(
                    EmployeeOrder.status == OrderStatus.COMPLETE
                )
                if employee_orders_db is not None:
                    for employee_order in employee_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == employee_order.order_line_id,
                        ).first()
                        employee_details_db = EmployeeDetails.query.filter(
                            EmployeeDetails.employee_login_id
                            == employee_order.employee_id,
                        ).first()
                        if order_line_db is not None:
                            order_head_db = OrderHead.query.filter(
                                OrderHead.id == order_line_db.order_head_id,
                            ).first()
                            if (
                                order_head_db is not None
                                and order_head_db.id not in orders
                            ):
                                orders.append(order_head_db.id)
                                data["table_2"].append(
                                    {
                                        "order_id": order_head_db.id,
                                        "date": f"{order_head_db.created_at.date()}",
                                        "name": f"{employee_details_db.first_name} {employee_details_db.last_name}",
                                        "price": f"{order_head_db.price if order_line_db.type is True else order_head_db.price*-1}",
                                        "type1": "Internal",
                                        "type2": f"{'POS' if order_line_db.type is True else 'Return'}",
                                    }
                                )

                if len(data["table_1"]) > 0:
                    data["table_1"] = sorted(
                        data["table_1"], key=lambda d: d["order_id"]
                    )
                if len(data["table_2"]) > 0:
                    data["table_2"] = sorted(
                        data["table_2"], key=lambda d: d["order_id"], reverse=True
                    )

                page_name = "employee_orders.html"
                path = os.path.join(page_name)
                return render_template(path, data=data)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/orderView/<int:order_id>/<action>", methods=[GET])
def employeeViewOrderInfo(order_id: int, action: str):
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                employee_detail_db = EmployeeDetails.query.filter(
                    EmployeeDetails.employee_login_id == employee_login_db.id
                ).first()
                order_head_db = OrderHead.query.filter(
                    OrderHead.id == order_id,
                ).first()
                if order_head_db is not None:
                    data = {
                        "order_id": order_head_db.id,
                        "word": BLANK,
                        "action": False,
                        "status": BLANK,
                        "first_name": BLANK,
                        "last_name": BLANK,
                        "phone": BLANK,
                        "address": BLANK,
                        "type": BLANK,
                        "order_details": [],
                    }

                    order_lines_db = OrderLine.query.filter(
                        OrderLine.order_head_id == order_head_db.id,
                    )
                    if order_lines_db is not None:
                        order_line_db = order_lines_db.first()
                        if order_line_db is not None:
                            customer_order_db = CustomerOrder.query.filter(
                                CustomerOrder.order_line_id == order_line_db.id,
                            ).first()
                            if customer_order_db is not None:
                                if action == "+":
                                    for order_line_db in order_lines_db:
                                        customer_order_db = CustomerOrder.query.filter(
                                            CustomerOrder.order_line_id
                                            == order_line_db.id,
                                        ).first()
                                        if customer_order_db is not None:
                                            customer_order_db.status = (
                                                OrderStatus.ORDER_ACCEPTED
                                            )
                                            product_db = Product.query.filter(
                                                Product.id == order_line_db.product_id,
                                            ).first()
                                            if product_db is not None:
                                                if (
                                                    product_db.available_quant
                                                    >= order_line_db.quant
                                                ):
                                                    product_db.available_quant = (
                                                        product_db.available_quant
                                                        - order_line_db.quant
                                                    )
                                                else:
                                                    diff = (
                                                        order_line_db.quant
                                                        - product_db.available_quant
                                                    ) * order_line_db.price
                                                    order_line_db.quant = (
                                                        product_db.available_quant
                                                    )
                                                    order_head_db.price - diff
                                            db.session.commit()
                                            db.session.refresh(order_head_db)

                                    customer_detail_db = CustomerDetails.query.filter(
                                        CustomerDetails.customer_login_id
                                        == customer_order_db.customer_id,
                                    ).first()
                                    if customer_detail_db is not None:
                                        email_send_ref = EmailSend(
                                            thread_name="Employee Order Accept",
                                            email=customer_detail_db.emailID,
                                            cc=employee_detail_db.emailID,
                                            subject=f"{server_name} | Order Accepted | {order_head_db.id}",
                                            body=f"""
                                            Hi {customer_detail_db.first_name},
                                        
                                            Your Online order : {order_head_db.id}
                                            Is being processed by {employee_detail_db.first_name}
                                            Order Type : {'Home Delivery' if customer_order_db.delivery == 'HD' else 'In Store Pick Up'}
                                            Amount: {order_head_db.price}
                                            
                                            Thanks and Regards,
                                            Bot.
                                            """,
                                        )
                                        email_send_ref.start()

                                elif action == "-":
                                    for order_line_db in order_lines_db:
                                        customer_order_db = CustomerOrder.query.filter(
                                            CustomerOrder.order_line_id
                                            == order_line_db.id,
                                        ).first()
                                        if customer_order_db is not None:
                                            customer_order_db.status = (
                                                OrderStatus.ORDER_REJECTED
                                            )
                                            order_head_db.price = 0
                                            db.session.commit()
                                            db.session.refresh(order_head_db)

                                    customer_detail_db = CustomerDetails.query.filter(
                                        CustomerDetails.customer_login_id
                                        == customer_order_db.customer_id,
                                    ).first()
                                    if customer_detail_db is not None:
                                        email_send_ref = EmailSend(
                                            thread_name="Employee Order Reject",
                                            email=customer_detail_db.emailID,
                                            cc=employee_detail_db.emailID,
                                            subject=f"{server_name} | Order Rejected | {order_head_db.id}",
                                            body=f"""
                                            Hi {customer_detail_db.first_name},
                                    
                                            Your Online order : {order_head_db.id}
                                            Has being rejected by {employee_detail_db.first_name},
                                            due to stock shortage.
                                            Order Type : {'Home Delivery' if customer_order_db.delivery == 'HD' else 'In Store Pick Up'}
                                    
                                            Thanks and Regards,
                                            Bot.
                                            """,
                                        )
                                        email_send_ref.start()

                                else:
                                    pass

                                customer_detail_db = CustomerDetails.query.filter(
                                    CustomerDetails.customer_login_id
                                    == customer_order_db.customer_id,
                                ).first()
                                if customer_detail_db is not None:
                                    data["word"] = "Customer"
                                    data["type"] = (
                                        "Home Delivery"
                                        if customer_order_db.delivery == "HD"
                                        else "In Store Pick Up"
                                    )
                                    data["status"] = customer_order_db.status
                                    if (
                                        customer_order_db.status
                                        == OrderStatus.ORDER_COMPLETE
                                    ):
                                        data["action"] = True
                                    data[
                                        "first_name"
                                    ] = customer_detail_db.first_name.capitalize()
                                    data[
                                        "last_name"
                                    ] = customer_detail_db.last_name.capitalize()
                                    data["phone"] = customer_detail_db.phoneNumber
                                    data["address"] = customer_detail_db.address

                            emp_order_db = EmployeeOrder.query.filter(
                                EmployeeOrder.order_line_id == order_line_db.id,
                            ).first()
                            if emp_order_db is not None:
                                emp_detail_db = EmployeeDetails.query.filter(
                                    EmployeeDetails.employee_login_id
                                    == emp_order_db.employee_id,
                                ).first()
                                if emp_detail_db is not None:
                                    data["word"] = "Employee"
                                    data["type"] = (
                                        "POS"
                                        if order_line_db.type is True
                                        else "Return"
                                    )
                                    data["status"] = emp_order_db.status
                                    data[
                                        "first_name"
                                    ] = emp_detail_db.first_name.capitalize()
                                    data[
                                        "last_name"
                                    ] = emp_detail_db.last_name.capitalize()
                                    data["phone"] = emp_detail_db.phoneNumber
                                    data["address"] = emp_detail_db.address

                        count = 0
                        for order_line_db in order_lines_db:
                            count = count + 1
                            product_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            if product_db is not None:
                                data["order_details"].append(
                                    {
                                        "sl_no": count,
                                        "name": product_db.name,
                                        "price": order_line_db.price,
                                        "qty": order_line_db.quant,
                                        "sub": order_line_db.price
                                        * order_line_db.quant,
                                    }
                                )
                    page_name = "employee_viewOrderInfo.html"
                    path = os.path.join(page_name)
                    return render_template(path, data=data)
                else:
                    flash(f"Order Id: {order_id}")
                    flash("Invalid Id")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination="employeeOrders", cookies=cookies)
                    return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    elif req_method == POST:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                employee_orders_db = EmployeeOrder.query.filter(
                    EmployeeOrder.employee_id == employee_login_db.id,
                    EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )
                if employee_orders_db is not None and employee_orders_db.count() > 0:
                    price = 0
                    order_content_str = []
                    for employee_order in employee_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == employee_order.order_line_id
                        ).first()
                        if order_line_db is not None:
                            price = price + (order_line_db.quant * order_line_db.price)
                            product_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            if product_db is not None:
                                if len(order_content_str) <= 0:
                                    order_content_str.append(
                                        "{}\t\t{}\t\t{}\t\t{}".format(
                                            "Product Name",
                                            "Quantity",
                                            "Price per Unit",
                                            "Subtotal",
                                        )
                                    )
                                order_content_str.append(
                                    "{}\t\t\t{}\t\t\t{}\t\t\t{}".format(
                                        product_db.name,
                                        order_line_db.quant,
                                        order_line_db.price,
                                        order_line_db.quant * order_line_db.price,
                                    )
                                )
                    order_head_db = OrderHead(
                        price=price,
                    )
                    db.session.add(order_head_db)
                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()
                    db.session.refresh(order_head_db)

                    for employee_order in employee_orders_db:
                        employee_order.status = OrderStatus.COMPLETE
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == employee_order.order_line_id
                        ).first()
                        if order_line_db is not None:
                            order_line_db.order_head_id = order_head_db.id

                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()

                    emp_details_db = EmployeeDetails.query.filter(
                        EmployeeDetails.employee_login_id == employee_login_db.id,
                    ).first()
                    if emp_details_db is not None:
                        body = f"""
                            Hi {emp_details_db.first_name},
    
                            You have placed an Order from POS.
    
                            Order ID : {order_head_db.id}
    
                            Order Contents are
                            """
                        for order in order_content_str:
                            body = (
                                body
                                + f"""
                                {order}
                                """
                            )
                        body = (
                            body
                            + f"""
                            Total : {order_head_db.price}
    
                            Thanks and Regards,
                            Bot.
                            """
                        )
                        email_send_ref = EmailSend(
                            thread_name="Employee Order Creation",
                            email=emp_details_db.emailID,
                            subject=f"{server_name} | Employee | Order Created | {order_head_db.id}",
                            body=body,
                        )
                        email_send_ref.start()

                    flash(f"Order ID : {order_head_db.id}")
                    flash(f"Order Created")
                cookies = [
                    [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="employeePosTerminal", cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employeePosTerminal", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


class EmployeeReturnAdd:
    def __init__(self, prod_id: int):
        self.prod_id = prod_id


@app.route("/employee/returnItemsAdd", methods=[POST])
def employeeReturnItemsAdd():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == POST:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                form_data = request.form
                emp_ret_add_ref = EmployeeReturnAdd(prod_id=int(form_data["productID"]))
                product_db = Product.query.filter(
                    Product.id == emp_ret_add_ref.prod_id,
                ).first()
                if product_db is not None:
                    flag_item_exists = False
                    emp_orders_db = EmployeeOrder.query.filter(
                        EmployeeOrder.employee_id == employee_login_db.id,
                        EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                    )
                    if emp_orders_db is not None:
                        for emp_order_db in emp_orders_db:
                            order_line_db = OrderLine.query.filter(
                                OrderLine.id == emp_order_db.order_line_id,
                                OrderLine.type == False,
                                OrderLine.product_id == product_db.id,
                            ).first()
                            if order_line_db is not None:
                                flag_item_exists = True

                    if flag_item_exists:
                        flash(f"Product ID : [{product_db.id}] {product_db.name}")
                        flash("Item Exists in Cart")
                    else:
                        order_line_db = OrderLine(
                            product_id=product_db.id,
                            quant=0,
                            price=0,
                            type=False,
                        )

                        db.session.add(order_line_db)
                        try:
                            db.session.commit()
                        except sqlite3.OperationalError as e:
                            print(f"Error : {str(e)}")
                            sleep(1)
                            db.session.commit()
                        db.session.refresh(order_line_db)

                        emp_order_db = EmployeeOrder(
                            order_line_id=order_line_db.id,
                            employee_id=employee_login_db.id,
                            status=OrderStatus.ORDER_INCOMPLETE,
                        )
                        db.session.add(emp_order_db)
                        try:
                            db.session.commit()
                        except sqlite3.OperationalError as e:
                            print(f"Error : {str(e)}")
                            sleep(1)
                            db.session.commit()

                        flash(f"Product ID : [{product_db.id}] {product_db.name}")
                        flash("Added to Cart")
                else:
                    flash(f"Product ID : {emp_ret_add_ref.prod_id}")
                    flash("Invalid ID")
                cookies = [
                    [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="employeeReturnItems", cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/returnItemsDel/<int:order_id>", methods=[GET])
def employeeReturnItemsDel(order_id: int):
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                if order_id == 0:
                    emp_orders_db = EmployeeOrder.query.filter(
                        EmployeeOrder.employee_id == employee_login_db.id,
                        EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                    )
                    for emp_order_db in emp_orders_db:
                        db.session.delete(emp_order_db)
                    flash("Deleted all Items")
                else:
                    emp_order_db = EmployeeOrder.query.filter(
                        EmployeeOrder.employee_id == employee_login_db.id,
                        EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                        EmployeeOrder.order_line_id == order_id,
                    ).first()
                    if emp_order_db is not None:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == emp_order_db.order_line_id,
                            OrderLine.type == False,
                        ).first()
                        if order_line_db is not None:
                            prod_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            if prod_db is not None:
                                flash(f"Product : [{prod_db.id}] {prod_db.name}")
                                flash("Deleted from Cart")
                        db.session.delete(emp_order_db)

                try:
                    db.session.commit()
                except sqlite3.OperationalError as e:
                    print(f"Error : {str(e)}")
                    sleep(1)
                    db.session.commit()

                cookies = [
                    [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="employeeReturnItems", cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


class EmplpyeeReturnItemEdit:
    def __init__(self, price: float, qunt: int):
        self.price = price
        self.quant = qunt


@app.route("/employee/returnItemsEdit/<int:order_id>", methods=[POST])
def employeeReturnItemsEdit(order_id: int):
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == POST:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                form_data = request.form
                edit_ref = EmplpyeeReturnItemEdit(
                    price=float(form_data["prod_price"]),
                    qunt=int(form_data["prod_quant"]),
                )
                if order_id == 0:
                    flash(f"Order Id : {order_id}")
                    flash("Invalid ID")
                else:
                    emp_order_db = EmployeeOrder.query.filter(
                        EmployeeOrder.employee_id == employee_login_db.id,
                        EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                        EmployeeOrder.order_line_id == order_id,
                    ).first()
                    if emp_order_db is not None:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == emp_order_db.order_line_id,
                            OrderLine.type == False,
                        ).first()
                        if order_line_db is not None:
                            order_line_db.price = edit_ref.price
                            order_line_db.quant = edit_ref.quant
                            prod_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            if prod_db is not None:
                                flash(f"Product : [{prod_db.id}] {prod_db.name}")
                            flash("Cart Updated")

                            try:
                                db.session.commit()
                            except sqlite3.OperationalError as e:
                                print(f"Error : {str(e)}")
                                sleep(1)
                                db.session.commit()

                cookies = [
                    [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="employeeReturnItems", cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/returnItems", methods=[GET, POST])
def employeeReturnItems():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                data = []
                emp_orders_db = EmployeeOrder.query.filter(
                    EmployeeOrder.employee_id == employee_login_db.id,
                    EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )
                if emp_orders_db is not None:
                    count = 0
                    for emp_order_db in emp_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == emp_order_db.order_line_id,
                            OrderLine.type == False,
                        ).first()
                        if order_line_db is not None:
                            count = count + 1
                            product_db = Product.query.filter(
                                Product.id == order_line_db.product_id,
                            ).first()
                            if product_db is not None:
                                data.append(
                                    {
                                        "prod_id": product_db.id,
                                        "prod_name": product_db.name,
                                        "prod_return": f"{'Yes' if product_db.accp_return is True else 'No'}",
                                        "price": order_line_db.price,
                                        "quant": order_line_db.quant,
                                        "sub": f"{order_line_db.price * order_line_db.quant}",
                                        "order_id": order_line_db.id,
                                        "sl_no": count,
                                        "readonly": f"{'readonly' if product_db.accp_return is False else BLANK}",
                                        "disabled": f"{'disabled' if product_db.accp_return is False else BLANK}",
                                    }
                                )
                page_name = "employee_returnItems.html"
                path = os.path.join(page_name)
                return render_template(path, data=data)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    elif req_method == POST:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                emp_orders_db = EmployeeOrder.query.filter(
                    EmployeeOrder.employee_id == employee_login_db.id,
                    EmployeeOrder.status == OrderStatus.ORDER_INCOMPLETE,
                )
                order_content_str = []
                if emp_orders_db is not None:
                    order_head_db = OrderHead(price=0)
                    count = 0
                    for emp_order_db in emp_orders_db:
                        order_line_db = OrderLine.query.filter(
                            OrderLine.id == emp_order_db.order_line_id,
                            OrderLine.type == False,
                        ).first()
                        if order_line_db is not None:
                            if len(order_content_str) <= 0:
                                order_content_str.append(
                                    "{}\t\t{}\t\t{}\t\t{}".format(
                                        "Product Name",
                                        "Quantity",
                                        "Price per Unit",
                                        "Subtotal",
                                    )
                                )
                            product_db = Product.query.filter(
                                Product.id == order_line_db.product_id
                            ).first()
                            if product_db is not None:
                                order_content_str.append(
                                    "{}\t\t\t{}\t\t\t{}\t\t\t{}".format(
                                        product_db.name,
                                        order_line_db.quant,
                                        order_line_db.price,
                                        order_line_db.quant * order_line_db.price,
                                    )
                                )
                            count = count + 1
                            emp_order_db.status = OrderStatus.COMPLETE
                            order_head_db.price = order_head_db.price + (
                                order_line_db.quant * order_line_db.price
                            )
                    if count > 0:
                        db.session.add(order_head_db)
                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()

                    if count > 0:
                        db.session.refresh(order_head_db)

                        emp_details_db = EmployeeDetails.query.filter(
                            EmployeeDetails.employee_login_id == employee_login_db.id,
                        ).first()
                        if emp_details_db is not None:
                            body = f"""
                            Hi {emp_details_db.first_name},
                        
                            You have placed an Order from POS => Return Order.
                        
                            Order ID : {order_head_db.id}
                        
                            Order Contents are
                            """
                            for order in order_content_str:
                                body = (
                                    body
                                    + f"""
                            {order}\n"""
                                )
                            body = (
                                body
                                + f"""
                            Total : {order_head_db.price}
                        
                            Thanks and Regards,
                            Bot.
                            """
                            )

                            email_send_ref = EmailSend(
                                thread_name="Employee Order Creation",
                                email=emp_details_db.emailID,
                                subject=f"{server_name} | Employee | Order Created | Return | {order_head_db.id}",
                                body=body,
                            )
                            email_send_ref.start()

                        emp_orders_db = EmployeeOrder.query.filter(
                            EmployeeOrder.employee_id == employee_login_db.id,
                            EmployeeOrder.status == OrderStatus.COMPLETE,
                        )
                        for emp_order_db in emp_orders_db:
                            order_line_db = OrderLine.query.filter(
                                OrderLine.id == emp_order_db.order_line_id,
                                OrderLine.type == False,
                                OrderLine.order_head_id == None,
                            ).first()
                            if order_line_db is not None:
                                order_line_db.order_head_id = order_head_db.id
                                product_db = Product.query.filter(
                                    Product.id == order_line_db.product_id,
                                ).first()
                                if product_db is not None:
                                    product_db.available_quant = (
                                        product_db.available_quant + order_line_db.quant
                                    )

                        try:
                            db.session.commit()
                        except sqlite3.OperationalError as e:
                            print(f"Error : {str(e)}")
                            sleep(1)
                            db.session.commit()

                        flash(f"Order ID : {order_head_db.id}")
                        flash("Return Order Placed")
                cookies = [
                    [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="employeeReturnItems", cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="employee_signin", cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="employee_signin", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/employee/logout", methods=[GET, POST])
def employeeLogout():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        cookies = [
            [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
        ]
        redirect = _redirect(destination="employee_signin", cookies=cookies)
        return redirect, 302
    else:
        abort(401)


# ======================
# Routing Admin


class AdminSignin:
    def __init__(self, login_id: str, password: str):
        self.login_id = login_id
        self.password = password
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password.encode("utf-8"))
        self.password = password_hash.hexdigest()


@app.route("/admin", methods=[GET, POST])
def adminSignIn():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_ADMIN])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_ADMIN] is not None:
            # Cookie Present
            admin_login_db = AdminLogin.query.filter(
                AdminLogin.user_name == req_cookies[AUTH_COOKIE_ADMIN],
            ).first()
            if admin_login_db is not None:
                # Cookie is okay
                cookies = [
                    [AUTH_COOKIE_ADMIN, req_cookies[AUTH_COOKIE_ADMIN], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination="adminWelcome", cookies=cookies)
                return redirect, 302
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="adminSignIn", cookies=cookies)
                return redirect, 302
        else:
            # No cookie present
            page_name = "admin_signin.html"
            path = os.path.join(page_name)
            return render_template(path)
    elif req_method == POST:
        form_data = request.form
        admin_signin_ref = AdminSignin(
            login_id=form_data["loginID"],
            password=form_data["password"],
        )
        admin_login_db = AdminLogin.query.filter(
            AdminLogin.user_name == admin_signin_ref.login_id.upper(),
            AdminLogin.password_hash == admin_signin_ref.password,
        ).first()
        if admin_login_db is not None:
            cookies = [
                [AUTH_COOKIE_ADMIN, admin_login_db.user_name, EXPIRE_1_WEEK],
            ]
            redirect = _redirect(destination="adminWelcome", cookies=cookies)
            return redirect, 302
        else:
            flash(INVALID_CRED)
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="adminSignIn", cookies=cookies)
            return redirect, 302
    else:
        abort(401)


@app.route("/admin/welcome", methods=[GET])
def adminWelcome():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_ADMIN])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_ADMIN] is not None:
            # Cookie Present
            admin_login_db = AdminLogin.query.filter(
                AdminLogin.user_name == req_cookies[AUTH_COOKIE_ADMIN],
            ).first()
            if admin_login_db is not None:
                # Cookie is okay
                page_name = "admin_welcome.html"
                path = os.path.join(page_name)
                return render_template(path)
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="adminSignIn", cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="adminSignIn", cookies=cookies)
            return redirect, 302
    else:
        abort(401)


class AdminUserAcess:
    def __init__(
        self, first_name: str, phone: str, last_name: str, email: str, password: str
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.password = password
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password.encode("utf-8"))
        self.password = password_hash.hexdigest()


@app.route("/admin/userAccess", methods=[GET, POST])
def adminUserAccess():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_ADMIN])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_ADMIN] is not None:
            # Cookie Present
            admin_login_db = AdminLogin.query.filter(
                AdminLogin.user_name == req_cookies[AUTH_COOKIE_ADMIN],
            ).first()
            if admin_login_db is not None:
                # Cookie is okay
                page_name = "admin_userAccess.html"
                emp_details_db = EmployeeDetails.query.all()
                data_send = []
                for emp in emp_details_db:
                    data_send.append(
                        {
                            "id": emp.employee_login_id,
                            "first_name": emp.first_name,
                            "last_name": emp.last_name,
                            "email": emp.emailID,
                            "phoneNumber": emp.phoneNumber,
                        }
                    )
                path = os.path.join(page_name)
                return render_template(path, data=data_send)
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="adminSignIn", cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="adminSignIn", cookies=cookies)
            return redirect, 302
    elif req_method == POST:
        if req_cookies[AUTH_COOKIE_ADMIN] is not None:
            # Cookie Present
            admin_login_db = AdminLogin.query.filter(
                AdminLogin.user_name == req_cookies[AUTH_COOKIE_ADMIN],
            ).first()
            if admin_login_db is not None:
                # Cookie is okay
                form_data = request.form
                admin_user_access_ref = AdminUserAcess(
                    first_name=form_data["first_name"],
                    last_name=form_data["last_name"],
                    email=form_data["email"],
                    password=form_data["password"],
                    phone=form_data["mobile"],
                )
                emp_login_db = EmployeeLogin.query.filter(
                    EmployeeLogin.user_name == admin_user_access_ref.email.upper(),
                ).first()
                if emp_login_db is not None:
                    # User exists
                    flash("Email Id Exists !")
                    cookies = [
                        [
                            AUTH_COOKIE_ADMIN,
                            req_cookies[AUTH_COOKIE_ADMIN],
                            EXPIRE_1_WEEK,
                        ],
                    ]
                    redirect = _redirect(destination="adminUserAccess", cookies=cookies)
                    return redirect, 302
                else:
                    # Create Employee
                    emp_login_db = EmployeeLogin(
                        user_name=admin_user_access_ref.email.upper(),
                        password_hash=admin_user_access_ref.password,
                    )
                    db.session.add(emp_login_db)
                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()
                    db.session.refresh(emp_login_db)
                    emp_details_db = EmployeeDetails(
                        first_name=admin_user_access_ref.first_name,
                        last_name=admin_user_access_ref.last_name,
                        emailID=admin_user_access_ref.email,
                        phoneNumber=admin_user_access_ref.phone,
                        employee_login_id=emp_login_db.id,
                    )
                    db.session.add(emp_details_db)
                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()

                    email_send_ref = EmailSend(
                        thread_name="Employee Creation",
                        email=admin_user_access_ref.email,
                        subject=f"{server_name} | Employee Account Created",
                        body=f"""
                        Hi {admin_user_access_ref.first_name},
                        
                        Welcome to {server_name}

                        User ID : {admin_user_access_ref.email}
                        Password : {form_data["password"]}

                        Thanks and Regards,
                        Bot.
                        """,
                    )
                    email_send_ref.start()

                    flash(
                        f"Employee : [{emp_details_db.employee_login_id}] {emp_details_db.first_name} {emp_details_db.last_name}"
                    )
                    flash("Employee Added")
                    cookies = [
                        [
                            AUTH_COOKIE_ADMIN,
                            req_cookies[AUTH_COOKIE_ADMIN],
                            EXPIRE_1_WEEK,
                        ],
                    ]
                    redirect = _redirect(destination="adminUserAccess", cookies=cookies)
                    return redirect, 302
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="adminSignIn", cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="adminSignIn", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


class AdminEditEmployee:
    def __init__(self, firstName, lastName, email, mobile, psw):
        self.first_name = firstName
        self.last_name = lastName
        self.email = email
        self.phone = mobile
        self.password = psw
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password.encode("utf-8"))
        self.password = password_hash.hexdigest()


@app.route("/admin/editEmployee/<int:empid>", methods=[GET, POST])
def admin_editEmployee(empid: int):
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_ADMIN])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_ADMIN] is not None:
            # Cookie Present
            admin_login_db = AdminLogin.query.filter(
                AdminLogin.user_name == req_cookies[AUTH_COOKIE_ADMIN],
            ).first()
            if admin_login_db is not None:
                # Cookie is okay
                employee_login_db = EmployeeLogin.query.filter(
                    EmployeeLogin.id == empid,
                ).first()
                if employee_login_db is not None:
                    employee_details_db = EmployeeDetails.query.filter(
                        EmployeeDetails.employee_login_id == employee_login_db.id,
                    ).first()
                    if employee_details_db is not None:
                        data = {
                            "id": employee_login_db.id,
                            "first_name": employee_details_db.first_name,
                            "last_name": employee_details_db.last_name,
                            "email": employee_details_db.emailID,
                            "mobile": employee_details_db.phoneNumber,
                        }
                        page_name = "admin_editProfile.html"
                        path = os.path.join(page_name)
                        return render_template(path, data=data)

            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="adminSignIn", cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="adminSignIn", cookies=cookies)
            return redirect, 302

    elif req_method == POST:
        recepients = []
        if req_cookies[AUTH_COOKIE_ADMIN] is not None:
            # Cookie Present
            admin_login_db = AdminLogin.query.filter(
                AdminLogin.user_name == req_cookies[AUTH_COOKIE_ADMIN],
            ).first()
            if admin_login_db is not None:
                # Cookie is okay
                form_data = request.form
                admin_edit_employee_ref = AdminEditEmployee(
                    firstName=form_data["firstName"],
                    lastName=form_data["lastName"],
                    email=form_data["email"],
                    mobile=form_data["mobile"],
                    psw=form_data["psw"],
                )
                emp_login_db = EmployeeLogin.query.filter(
                    EmployeeLogin.id == empid,
                ).first()
                if emp_login_db is not None:
                    # User exists
                    employee_details_db = EmployeeDetails.query.filter(
                        EmployeeDetails.employee_login_id == emp_login_db.id,
                    ).first()
                    if employee_details_db.emailID != admin_edit_employee_ref.email:
                        emp_login_db_other = EmployeeLogin.query.filter(
                            EmployeeLogin.user_name == admin_editEmployee.email.upper(),
                        ).first()
                        if emp_login_db_other is not None:
                            if emp_login_db_other.id != emp_login_db.id:
                                flash("Email Id Exists !")
                                cookies = [
                                    [
                                        AUTH_COOKIE_ADMIN,
                                        req_cookies[AUTH_COOKIE_ADMIN],
                                        EXPIRE_1_WEEK,
                                    ],
                                ]
                                redirect = _redirect(
                                    destination="admin_editEmployee", cookies=cookies
                                )
                                return redirect, 302
                        else:
                            recepients.append(employee_details_db.emailID)  # Old Email
                            employee_details_db.emailID = admin_edit_employee_ref.email
                            emp_login_db.user_name = admin_edit_employee_ref.email()
                            # Send email to both emails
                            recepients.append(employee_details_db.emailID)  # New Email
                    else:
                        recepients.append(employee_details_db.emailID)  # Old Email

                    actual_password = form_data["psw"]
                    if (
                        actual_password != BLANK
                        and emp_login_db.password_hash != admin_edit_employee_ref
                    ):
                        emp_login_db.password_hash = admin_edit_employee_ref.password
                    else:
                        actual_password = None

                    employee_details_db.first_name = admin_edit_employee_ref.first_name
                    employee_details_db.last_name = admin_edit_employee_ref.last_name
                    employee_details_db.phoneNumber = admin_edit_employee_ref.phone

                    for recepient in recepients:
                        email_send_ref = EmailSend(
                            thread_name="Employee Updation",
                            email=recepient,
                            cc=admin_login_db.user_name,
                            subject=f"{server_name} | Employee Account Updated",
                            body=f"""
                            Hi {employee_details_db.first_name},
    
                            Your employee account has been updated by admin {req_cookies[AUTH_COOKIE_ADMIN]}.
                            
                            First Name : {employee_details_db.first_name}
                            Last Name : {employee_details_db.last_name}
                            Email Id : {employee_details_db.emailID}
                            Phone Number : {employee_details_db.phoneNumber}
                            Password : {actual_password if actual_password is not None else "Not Changed"}
    
                            Thanks and Regards,
                            Bot.
                            """,
                        )
                        email_send_ref.start()

                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()
                    flash(
                        f"Employee: [{employee_details_db.employee_login_id}] {employee_details_db.first_name} {employee_details_db.last_name}"
                    )
                    flash("Employee Account Updated")
                    cookies = [
                        [
                            AUTH_COOKIE_ADMIN,
                            req_cookies[AUTH_COOKIE_ADMIN],
                            EXPIRE_1_WEEK,
                        ],
                    ]
                    redirect = _redirect(destination="adminUserAccess", cookies=cookies)
                    return redirect, 302

                else:
                    flash("Incorrect Employee Id")
                    cookies = [
                        [
                            AUTH_COOKIE_ADMIN,
                            req_cookies[AUTH_COOKIE_ADMIN],
                            EXPIRE_1_WEEK,
                        ],
                    ]
                    redirect = _redirect(destination="adminUserAccess", cookies=cookies)
                    return redirect, 302

            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="adminSignIn", cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="adminSignIn", cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route("/admin/deleteEmployee/<int:empid>", methods=[GET])
def admin_deleteEmployee(empid: int):
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_ADMIN])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_ADMIN] is not None:
            # Cookie Present
            admin_login_db = AdminLogin.query.filter(
                AdminLogin.user_name == req_cookies[AUTH_COOKIE_ADMIN],
            ).first()
            if admin_login_db is not None:
                # Cookie is okay
                emp_login_db = EmployeeLogin.query.filter(
                    EmployeeLogin.id == empid,
                ).first()
                if emp_login_db is not None:
                    flash(f"Employee {emp_login_db.user_name} deleted")
                    emp_details_db = EmployeeDetails.query.filter(
                        EmployeeDetails.employee_login_id == empid,
                    ).first()
                    if emp_details_db is not None:
                        email_send_ref = EmailSend(
                            thread_name="Employee Deletion",
                            email=emp_details_db.emailID,
                            cc=admin_login_db.user_name,
                            subject=f"{server_name} | Employee Account Deleted",
                            body=f"""
                            Hi {emp_details_db.first_name},
                            
                            Your employee access for user {emp_details_db.emailID}
                            has been revoked.
                            Thanks for being a valued employee.
    
                            Thanks and Regards,
                            Bot.
                            """,
                        )
                        email_send_ref.start()

                    db.session.delete(emp_login_db)
                    try:
                        db.session.commit()
                    except sqlite3.OperationalError as e:
                        print(f"Error : {str(e)}")
                        sleep(1)
                        db.session.commit()

                    cookies = [
                        [
                            AUTH_COOKIE_ADMIN,
                            req_cookies[AUTH_COOKIE_ADMIN],
                            EXPIRE_1_WEEK,
                        ],
                    ]
                    redirect = _redirect(destination="adminUserAccess", cookies=cookies)
                    return redirect, 302
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination="adminSignIn", cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination="adminSignIn", cookies=cookies)
            return redirect, 302
    else:
        abort(401)


@app.route("/admin/logout", methods=[GET])
def admin_logout():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_ADMIN])

    if req_method == GET:
        cookies = [
            [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
        ]
        redirect = _redirect(destination="adminSignIn", cookies=cookies)
        return redirect, 302
    else:
        abort(401)
