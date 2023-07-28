# ========================================================
# IMPORTS

import json
import os
from pathlib import Path

from flask import Flask, render_template, abort, request, make_response, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# ========================================================
# CONSTANTS

DATABASE = "DATABASE"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"
HOST = "HOST"
PORT = "PORT"
NAME = "NAME"
GET = "GET"
POST = "POST"
DEBUG = True

# ========================================================

PROJECT_DIR = Path(__file__).resolve().parent

# ========================================================
# DATABASE + APP

try:
    with open(os.path.join(PROJECT_DIR, "documents", "secret.json")) as secret:
        data = json.load(secret)
        if DEBUG:
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
    app = Flask(__name__)
except Exception as e:
    print(str(e))
    raise KeyboardInterrupt
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_CON
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db = SQLAlchemy(app)
    migrate = Migrate(app, db, command='migrate')


# ========================================================
# Models

# =========================
# Customer Models
class CustomerLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    customer_details = db.relationship('CustomerDetails', backref='customerlogin', lazy=True)
    customer_sales = db.relationship('CustomerSales', backref='customerlogin', lazy=True)

    def __repr__(self):
        return f"{self.email}"


class CustomerDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(String(50), nullable=False)
    last_name = db.Column(String(50), nullable=False)
    phoneNumber = db.Column(Integer, nullable=False)
    emailID = db.Column(String(100), nullable=False)
    address = db.Column(String(200), nullable=False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())

    customer_login_id = db.Column(db.Integer, db.ForeignKey( "customerlogin.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


class CustomerSales(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    customer_login_id = db.Column(db.Integer, db.ForeignKey( "customerlogin.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"SALE ID : {self.id}"

# =========================

# =========================

# =========================

# ========================================================
# Routing

@app.route('/', methods=[GET])
def landingPage() -> str:
    if request.method == GET:
        page_name = 'landingpage.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


# ======================

class CustomerPage():
    def __init__(self, login_id: str, password: str):
        self.login_id = login_id
        self.password = password


@app.route('/customer', methods=[GET, POST])
def customer_page() -> str:
    page_name_1 = 'customer_loginpage.html'
    page_name_2 = 'customer_OrderPlacement.html'
    if request.method == GET:
        path = os.path.join(page_name_1)
        return render_template(path)
    elif request.method == POST:
        form_data = request.form
        admin_page_ref = AdminPage(
            login_id=form_data["loginID"],
            password=form_data["password"],
        )
        path = os.path.join(page_name_2)
        return render_template(path)
    else:
        abort(401)


@app.route('/customer/SignUp', methods=[GET, POST])
def customer_SignUpp() -> str:
    if request.method == GET:
        page_name = 'customer_signup.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


@app.route('/customer/changeProfile', methods=[GET, POST])
def customer_changeProfile() -> str:
    if request.method == GET:
        page_name = 'customer_editProfile.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


# ======================


class AdminPage:
    def __init__(self, login_id: str, password: str):
        self.login_id = login_id
        self.password = password


@app.route('/admin', methods=[GET, POST])
def admin_page() -> str:
    page_name_1 = 'admin_signin.html'
    page_name_2 = 'admin_welcome.html'
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is not None:
                raise Exception("Cookie Found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie("auth", '', 0)
            res.headers['location'] = url_for('adminWelcome')
            return res, 302
        else:
            path = os.path.join(page_name_1)
            return render_template(path)
    elif request.method == POST:
        form_data = request.form
        admin_page_ref = AdminPage(
            login_id=form_data["loginID"],
            password=form_data["password"],
        )
        path = os.path.join(page_name_2)
        # return render_template(path)
        res = make_response()
        res.set_cookie("auth", "DATA HERE", 60 * 60 * 24 * 2)
        res.headers['location'] = url_for('adminWelcome')
        return res, 302
    else:
        abort(401)


@app.route('/admin/welcome', methods=[GET, POST])
def adminWelcome() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie("auth", '', 0)
            res.headers['location'] = url_for('admin_page')
            return res, 302
        else:
            page_name = 'admin_welcome.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/admin/inventory', methods=[GET, POST])
def adminInventory() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie("auth", '', 0)
            res.headers['location'] = url_for('admin_page')
            return res, 302
        else:
            page_name = 'admin_inventory.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/admin/posTerminal', methods=[GET, POST])
def adminPosTerminal() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie("auth", '', 0)
            res.headers['location'] = url_for('admin_page')
            return res, 302
        else:
            page_name = 'admin_posTerminal.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/admin/monthlyRevenue', methods=[GET, POST])
def adminMonthlyRevenue() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie("auth", '', 0)
            res.headers['location'] = url_for('admin_page')
            return res, 302
        else:
            page_name = 'admin_monthlyRevenue.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/admin/orders', methods=[GET, POST])
def adminOrders() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie("auth", '', 0)
            res.headers['location'] = url_for('admin_page')
            return res, 302
        else:
            page_name = 'admin_orders.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/admin/returnItems', methods=[GET, POST])
def adminreturnItems() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie("auth", '', 0)
            res.headers['location'] = url_for('admin_page')
            return res, 302
        else:
            page_name = 'admin_returnItems.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/admin/logout', methods=[GET, POST])
def adminLogout():
    if request.method == GET:
        res = make_response()
        res.set_cookie("auth", '', 0)
        res.headers['location'] = url_for('admin_page')
        return res, 302
    else:
        abort(401)

# ==========================================================
