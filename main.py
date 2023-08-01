# ========================================================
# IMPORTS
import base64
import hashlib
import json
import os
import random
import string
from pathlib import Path

# from cryptography.fernet import Fernet
from flask import Flask, render_template, abort, request, make_response, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, DateTime
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
BLANK = ''
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
        app.config['SECRET_KEY'] = server_secret
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
    __tablename__ = 'customer_login'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    customer_details = db.relationship('CustomerDetails', backref='customer_login', lazy=True, cascade='all, delete')
    customer_order = db.relationship('CustomerOrder', backref='customer_login', lazy=True, cascade='all, delete')

    def __repr__(self):
        return f"{self.email}"


class CustomerDetails(db.Model):
    __tablename__ = 'customer_details'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(String(50), nullable=False)
    last_name = db.Column(String(50), nullable=False)
    emailID = db.Column(String(100), nullable=False)
    phoneNumber = db.Column(Integer, nullable=False)
    address = db.Column(String(200), nullable=False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())

    customer_login_id = db.Column(db.Integer, db.ForeignKey("customer_login.id"), nullable=False)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


# =========================
# Admin Models
class AdminLogin(db.Model):
    __tablename__ = 'admin_login'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    admin_details = db.relationship('AdminDetails', backref='admin_login', lazy=True, cascade='all, delete')
    employee_login = db.relationship('EmployeeLogin', backref='admin_login', lazy=True, cascade='all, delete')

    def __repr__(self):
        return f"{self.email}"


class AdminDetails(db.Model):
    __tablename__ = 'admin_details'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    emailID = db.Column(db.String(100), nullable=False)
    phoneNumber = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    admin_login_id = db.Column(db.Integer, db.ForeignKey("admin_login.id"), nullable=False)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


# =========================
# Employee Models
class EmployeeLogin(db.Model):
    __tablename__ = 'employee_login'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    created_by = db.Column(db.Integer, db.ForeignKey("admin_login.id", ondelete="SET NULL"), nullable=True)

    employee_details = db.relationship('EmployeeDetails', backref='employee_login', lazy=True, cascade='all, delete')

    def __repr__(self):
        return f"{self.email}"


class EmployeeDetails(db.Model):
    __tablename__ = 'employee_details'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    emailID = db.Column(db.String(100), nullable=False)
    phoneNumber = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    employee_login_id = db.Column(db.Integer, db.ForeignKey("employee_login.id"), nullable=False)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


# =========================
# Product Models

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    available_quant = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    shelf_loc = db.Column(db.String(10), nullable=True)
    accp_return = db.Column(db.Boolean, nullable=True)
    reorder_quant = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    order = db.relationship('Order', backref='product', lazy=True, cascade='all, delete')

    def __repr__(self):
        return f"{self.id} {self.name}"


# =========================
# Order Models

class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    available_quant = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    shelf_loc = db.Column(db.String(10), nullable=True)
    accp_return = db.Column(db.Boolean, nullable=True)
    reorder_quant = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    order = db.relationship('CustomerOrder', backref='order', lazy=True, cascade='all, delete')

    def __repr__(self):
        return f"{self.id} {self.name}"


class CustomerOrder(db.Model):
    __tablename__ = 'customer_order'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer_login.id"), nullable=False)

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

@app.route('/', methods=[GET])
def landingPage() -> str:
    req_method = request.method
    if req_method == GET:
        page_name = 'landingpage.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


def _redirect(destination: str, cookies: list):
    res = make_response()
    for cookie in cookies:
        res.set_cookie(cookie[0], cookie[1], cookie[2])
    res.headers['location'] = url_for(destination)
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

@app.route('/customer', methods=[GET])
def customer_landing_page():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user is logged in
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='customer_signin', cookies=cookies)
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
                redirect = _redirect(destination='customer_OrderPlacement', cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
                return redirect, 302

    else:
        abort(401)


class CustomerSignin:
    def __init__(self, login_id: str, password: str):
        self.login_id = login_id.upper()
        self.password = password
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password.encode('utf-8'))
        self.password = password_hash.hexdigest()[:254]


@app.route('/customer/signin', methods=[GET, POST])
def customer_signin():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user is logged in
            page_name = 'customer_loginpage.html'
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
                redirect = _redirect(destination='customer_OrderPlacement', cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
                return redirect, 302

    elif req_method == POST:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user is logged in
            form_data = request.form
            customer_signin_ref = CustomerSignin(
                login_id=form_data['loginID'],
                password=form_data['password'],
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
                redirect = _redirect(destination='customer_OrderPlacement', cookies=cookies)
                return redirect, 302
            else:
                flash(INVALID_CRED)
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
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
                redirect = _redirect(destination='customer_OrderPlacement', cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
                return redirect, 302

    else:
        abort(401)


class CustomerOrderPlacement:
    def __init__(self):
        self.data = None


@app.route('/customer/orderplacement', methods=[GET, POST])
def customer_OrderPlacement():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user logged in
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='customer_signin', cookies=cookies)
            return redirect, 302
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE_CUST],
            ).first()
            if customer_login_db is not None:
                # Existing Cookie belongs to user in DB
                page_name = 'customer_OrderPlacement.html'
                path = os.path.join(page_name)
                return render_template(path)
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
                return redirect, 302

    elif req_method == POST:
        form_data = request.form
        print(form_data)
        abort(401)

    else:
        abort(401)


class CustomerSignup:
    def __init__(self, first_name: str, last_name: str, email: str, phone: str, address: str, password: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.password = password
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password.encode('utf-8'))
        self.password = password_hash.hexdigest()[:254]


@app.route('/customer/signup', methods=[GET, POST])
def customer_SignUp():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user logged in
            page_name = 'customer_signup.html'
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
                redirect = _redirect(destination='customer_OrderPlacement', cookies=cookies)
                return redirect, 302
            else:
                page_name = 'customer_signup.html'
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
            CustomerLogin.user_name == customer_signup_ref.email.upper()).first()
        if customer_login_db is not None:
            # If user exists -> Redirect to Signup Page
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            flash('Email ID Exists')
            redirect = _redirect(destination='customer_SignUp', cookies=cookies)
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
                address=customer_signup_ref.address
            )

            db.session.add(customer_login_db)
            db.session.commit()
            db.session.refresh(customer_login_db)
            customer_details_db.customer_login_id = customer_login_db.id
            db.session.add(customer_details_db)
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
                """
            )
            email_send_ref.start()

            # If New user -> Redirect to Order Placement Page
            cookies = [
                [AUTH_COOKIE_CUST, customer_login_db.user_name, EXPIRE_1_WEEK],
            ]
            redirect = _redirect(destination='customer_OrderPlacement', cookies=cookies)
            return redirect, 302

    else:
        abort(401)


class CustomerEditProfile:
    def __init__(self, first_name: str, last_name: str, email: str, mobile: str, address: str, psw_old: str, psw: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.mobile = mobile
        self.address = address
        self.password_old = psw_old
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password_old.encode('utf-8'))
        self.password_old = password_hash.hexdigest()[:254]
        self.password_new = psw
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password_new.encode('utf-8'))
        self.password_new = password_hash.hexdigest()[:254]


@app.route('/customer/editprofile', methods=[GET, POST])
def customer_editProfile():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user logged in
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='customer_signin', cookies=cookies)
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
                        'first_name': customer_details_db.first_name,
                        'last_name': customer_details_db.last_name,
                        'email': customer_details_db.emailID,
                        'mobile': customer_details_db.phoneNumber,
                        'address': customer_details_db.address,
                    }
                else:
                    data = {
                        'first_name': "Dummy Data",
                        'last_name': "Dummy Data",
                        'email': "Dummy Data",
                        'mobile': "Dummy Data",
                        'address': "Dummy Data",
                    }
                page_name = 'customer_editProfile.html'
                path = os.path.join(page_name)
                return render_template(path, data=data)
            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
                return redirect, 302

    elif req_method == POST:
        form_data = request.form
        if req_cookies[AUTH_COOKIE_CUST] is None:
            # No user logged in
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='customer_signin', cookies=cookies)
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
                    if customer_login_db.user_name != customer_edit_profile_ref.email.upper():
                        # Check if someone else has the same email id
                        customer_login_db_other = CustomerLogin.query.filter(
                            CustomerLogin.user_name == customer_edit_profile_ref.email.upper(),
                        ).first()
                        if customer_login_db_other is not None:
                            # Redirect to self using a message
                            if customer_login_db.id != customer_login_db_other.id:
                                flash('Email Id already in use')
                                cookies = [
                                    [AUTH_COOKIE_CUST, req_cookies[AUTH_COOKIE_CUST], EXPIRE_1_WEEK],
                                ]
                                redirect = _redirect(destination='customer_editProfile', cookies=cookies)
                                return redirect, 302
                            else:
                                customer_login_db.user_name = customer_edit_profile_ref.email.upper()

                    # Check if old and existing password matches
                    if customer_edit_profile_ref.password_old != customer_login_db.password_hash:
                        # Redirect to self using a message
                        flash('Existing Password is wrong')
                        cookies = [
                            [AUTH_COOKIE_CUST, req_cookies[AUTH_COOKIE_CUST], EXPIRE_1_WEEK],
                        ]
                        redirect = _redirect(destination='customer_editProfile', cookies=cookies)
                        return redirect, 302
                    else:
                        # Check if old password and new passwords are different
                        if customer_edit_profile_ref.password_old != customer_edit_profile_ref.password_new:
                            customer_login_db.password_hash = customer_edit_profile_ref.password_new

                    # Get related Customer Details Entry
                    customer_details_db = CustomerDetails.query.filter(
                        CustomerDetails.customer_login_id == customer_login_db.id,
                    ).first()
                    if customer_details_db is not None:
                        customer_details_db.first_name = customer_edit_profile_ref.first_name
                        customer_details_db.last_name = customer_edit_profile_ref.last_name
                        customer_details_db.emailID = customer_edit_profile_ref.email
                        customer_details_db.phoneNumber = customer_edit_profile_ref.mobile
                        customer_details_db.address = customer_edit_profile_ref.address

                        # Commit all changes
                        db.session.commit()

                        # Redirect to self using a message
                        flash('Update Successful')
                        cookies = [
                            [AUTH_COOKIE_CUST, req_cookies[AUTH_COOKIE_CUST], EXPIRE_1_WEEK],
                        ]
                        redirect = _redirect(destination='customer_editProfile', cookies=cookies)
                        return redirect, 302

            else:
                cookies = [
                    [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
                return redirect, 302
    else:
        abort(401)


@app.route('/customer/logout', methods=[GET])
def customerLogout():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        cookies = [
            [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
        ]
        redirect = _redirect(destination='customer_signin', cookies=cookies)
        return redirect, 302
    else:
        abort(401)


class CustomerForgotPassword:
    def __init__(self, email):
        self.email = email


@app.route('/customer/forget_password', methods=[GET, POST])
def customerForgotPWD():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_CUST])

    if req_method == GET:
        page_name = 'customer_forgotPwd.html'
        path = os.path.join(page_name)
        return render_template(path)
    elif req_method == POST:
        form_data = request.form
        customer_forgot_password_ref = CustomerForgotPassword(
            email=form_data["email"]
        )
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
            password_hash.update(new_password.encode('utf-8'))
            customer_login_db.password_hash = password_hash.hexdigest()[:254]
            db.session.commit()
            email_send_ref = EmailSend(
                thread_name="Forgot Password",
                email=customer_forgot_password_ref.email,
                subject=f"{server_name} | Reset Password",
                body=f"Your new password is : {new_password}"
            )
            email_send_ref.start()
            flash('New Password sent to Email id')
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='customerForgotPWD', cookies=cookies)
            return redirect, 302
        else:
            # Email not in Database
            flash('Email does not exist')
            cookies = [
                [AUTH_COOKIE_CUST, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='customerForgotPWD', cookies=cookies)
            return redirect, 302


# ======================
# Routing Employee

class EmployeeSignin:
    def __init__(self, login_id: str, password: str):
        self.login_id = login_id.upper()
        self.password = password
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password.encode('utf-8'))
        self.password = password_hash.hexdigest()[:254]


@app.route('/employee', methods=[GET, POST])
def employee_signin():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is None:
            # No user logged in
            page_name = 'employee_signin.html'
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
                redirect = _redirect(destination='employeeWelcome', cookies=cookies)
                return redirect, 302
            else:
                page_name = 'employee_signin.html'
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
                redirect = _redirect(destination='employeeWelcome', cookies=cookies)
                return redirect, 302
            else:
                # Wrong Credentials
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                flash(INVALID_CRED)
                redirect = _redirect(destination='employee_signin', cookies=cookies)
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
                redirect = _redirect(destination='employeeWelcome', cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                flash('Enter Credentials again !')
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302

    else:
        abort(401)


@app.route('/employee/welcome', methods=[GET, POST])
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
                page_name = 'employee_welcome.html'
                path = os.path.join(page_name)
                return render_template(path)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='employee_signin', cookies=cookies)
            return redirect, 302
    else:
        abort(401)


class EmployeeInventory:
    def __init__(self, name: str, price: str, shelf:str, quant_a: str, returns: str, quant_r: str):
        self.name = name.upper()
        self.price = float(price)
        self.quant_a = int(quant_a)
        self.quant_r = int(quant_r)
        self.returns = True if returns.upper() == "YES" else False
        self.shelf = shelf.upper()


@app.route('/employee/inventory', methods=[GET, POST])
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
                    data.append({
                        "id": product.id,
                        "name": product.name,
                        "price": product.price,
                        "quant_a": product.available_quant,
                        "shelf": product.shelf_loc,
                        "returns": "Yes" if product.accp_return is True else "No",
                        "quant_r": product.reorder_quant,
                    })
                page_name = 'employee_inventory.html'
                path = os.path.join(page_name)
                return render_template(path, data=data)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='employee_signin', cookies=cookies)
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
                    flash(f"Product Exists : {product_db.id}")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='employeeInventory', cookies=cookies)
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
                    db.session.commit()
                    db.session.refresh(product_db)

                    flash(f"Product Added : {product_db.id}")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='employeeInventory', cookies=cookies)
                    return redirect, 302
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='employee_signin', cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route('/employee/editItemInfo/<int:prod_id>', methods=[GET, POST])
def employeeEditItemInfo(prod_id:int):
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
                    page_name = 'employee_inventoryEdit.html'
                    path = os.path.join(page_name)
                    return render_template(path, data=data)
                else:
                    flash(f"Invalid Product Id : {prod_id}")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='employeeInventory', cookies=cookies)
                    return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='employee_signin', cookies=cookies)
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
                    db.session.commit()

                    flash(f"Product Info Updated : {product_db.id}")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='employeeInventory', cookies=cookies)
                    return redirect, 302
                else:
                    flash(f"Product does not Exist : {prod_id}")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='employeeInventory', cookies=cookies)
                    return redirect, 302
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='employee_signin', cookies=cookies)
            return redirect, 302

    else:
        abort(401)

@app.route('/employee/delItemInfo/<int:prod_id>', methods=[GET])
def employeeDelItemInfo(prod_id:int):
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

                    db.session.delete(product_db)
                    db.session.commit()

                    flash(f"Product Deleted : {prod_id}")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='employeeInventory', cookies=cookies)
                    return redirect, 302
                else:
                    flash(f"Invalid Product Id : {prod_id}")
                    cookies = [
                        [AUTH_COOKIE_EMP, req_cookies[AUTH_COOKIE_EMP], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='employeeInventory', cookies=cookies)
                    return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='employee_signin', cookies=cookies)
            return redirect, 302

    else:
        abort(401)

@app.route('/employee/posTerminal', methods=[GET, POST])
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
                page_name = 'employee_posTerminal.html'
                path = os.path.join(page_name)
                return render_template(path)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='employee_signin', cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route('/employee/monthlyRevenue', methods=[GET, POST])
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
                page_name = 'employee_monthlyRevenue.html'
                path = os.path.join(page_name)
                return render_template(path)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='employee_signin', cookies=cookies)
            return redirect, 302

    else:
        abort(401)

#
@app.route('/employee/orders', methods=[GET, POST])
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
                page_name = 'employee_orders.html'
                path = os.path.join(page_name)
                return render_template(path)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='employee_signin', cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route('/employee/returnItems', methods=[GET, POST])
def employeereturnItems():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE_EMP] is not None:
            # Check Cookie
            employee_login_db = EmployeeLogin.query.filter(
                EmployeeLogin.user_name == req_cookies[AUTH_COOKIE_EMP],
            ).first()
            if employee_login_db is not None:
                page_name = 'employee_returnItems.html'
                path = os.path.join(page_name)
                return render_template(path)
            else:
                cookies = [
                    [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='employee_signin', cookies=cookies)
                return redirect, 302
        else:
            cookies = [
                [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='employee_signin', cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route('/employee/logout', methods=[GET, POST])
def employeeLogout():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_EMP])

    if req_method == GET:
        cookies = [
            [AUTH_COOKIE_EMP, BLANK, EXPIRE_NOW],
        ]
        redirect = _redirect(destination='employee_signin', cookies=cookies)
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
        password_hash.update(self.password.encode('utf-8'))
        self.password = password_hash.hexdigest()


@app.route('/admin', methods=[GET, POST])
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
                redirect = _redirect(destination='adminWelcome', cookies=cookies)
                return redirect, 302
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='adminSignIn', cookies=cookies)
                return redirect, 302
        else:
            # No cookie present
            page_name = 'admin_signin.html'
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
            AdminLogin.password_hash == admin_signin_ref.password
        ).first()
        if admin_login_db is not None:
            cookies = [
                [AUTH_COOKIE_ADMIN, admin_login_db.user_name, EXPIRE_1_WEEK],
            ]
            redirect = _redirect(destination='adminWelcome', cookies=cookies)
            return redirect, 302
        else:
            flash(INVALID_CRED)
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='adminSignIn', cookies=cookies)
            return redirect, 302
    else:
        abort(401)


@app.route('/admin/welcome', methods=[GET])
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
                page_name = 'admin_welcome.html'
                path = os.path.join(page_name)
                return render_template(path)
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='adminSignIn', cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='adminSignIn', cookies=cookies)
            return redirect, 302
    else:
        abort(401)


class AdminUserAcess:
    def __init__(self, first_name: str, last_name: str, email: str, password: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        # Hash actual password
        password_hash = hashlib.sha1()
        password_hash.update(self.password.encode('utf-8'))
        self.password = password_hash.hexdigest()


@app.route('/admin/userAccess', methods=[GET, POST])
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
                page_name = 'admin_userAccess.html'
                emp_details_db = EmployeeDetails.query.all()
                data_send = []
                for emp in emp_details_db:
                    data_send.append({
                        "id": emp.employee_login_id,
                        "first_name": emp.first_name,
                        "last_name": emp.last_name,
                        "email": emp.emailID,
                    })
                path = os.path.join(page_name)
                return render_template(path, data=data_send)
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='adminSignIn', cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='adminSignIn', cookies=cookies)
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
                )
                emp_login_db = EmployeeLogin.query.filter(
                    EmployeeLogin.user_name == admin_user_access_ref.email.upper(),
                ).first()
                if emp_login_db is not None:
                    # User exists
                    flash("Email Id Exists !")
                    cookies = [
                        [AUTH_COOKIE_ADMIN, req_cookies[AUTH_COOKIE_ADMIN], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='adminUserAccess', cookies=cookies)
                    return redirect, 302
                else:
                    # Create Employee
                    emp_login_db = EmployeeLogin(
                        user_name=admin_user_access_ref.email.upper(),
                        password_hash=admin_user_access_ref.password
                    )
                    db.session.add(emp_login_db)
                    db.session.commit()
                    db.session.refresh(emp_login_db)
                    emp_details_db = EmployeeDetails(
                        first_name=admin_user_access_ref.first_name,
                        last_name=admin_user_access_ref.last_name,
                        emailID=admin_user_access_ref.email,
                        employee_login_id=emp_login_db.id
                    )
                    db.session.add(emp_details_db)
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
                        """
                    )
                    email_send_ref.start()

                    flash("Employee Added")
                    cookies = [
                        [AUTH_COOKIE_ADMIN, req_cookies[AUTH_COOKIE_ADMIN], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='adminUserAccess', cookies=cookies)
                    return redirect, 302
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='adminSignIn', cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='adminSignIn', cookies=cookies)
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
        password_hash.update(self.password.encode('utf-8'))
        self.password = password_hash.hexdigest()


@app.route('/admin/editEmployee/<int:empid>', methods=[GET, POST])
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
                        page_name = 'admin_editProfile.html'
                        path = os.path.join(page_name)
                        return render_template(path, data=data)

            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='adminSignIn', cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='adminSignIn', cookies=cookies)
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
                                    [AUTH_COOKIE_ADMIN, req_cookies[AUTH_COOKIE_ADMIN], EXPIRE_1_WEEK],
                                ]
                                redirect = _redirect(destination='admin_editEmployee', cookies=cookies)
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
                    if (actual_password != BLANK
                            and emp_login_db.password_hash != admin_edit_employee_ref):
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
                            """
                        )
                        email_send_ref.start()

                    db.session.commit()
                    flash("Employee Account Updated")
                    cookies = [
                        [AUTH_COOKIE_ADMIN, req_cookies[AUTH_COOKIE_ADMIN], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='adminUserAccess', cookies=cookies)
                    return redirect, 302

                else:
                    flash("Incorrect Employee Id")
                    cookies = [
                        [AUTH_COOKIE_ADMIN, req_cookies[AUTH_COOKIE_ADMIN], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='adminUserAccess', cookies=cookies)
                    return redirect, 302




            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='adminSignIn', cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='adminSignIn', cookies=cookies)
            return redirect, 302

    else:
        abort(401)


@app.route('/admin/deleteEmployee/<int:empid>', methods=[GET])
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
                    flash(f'Employee {emp_login_db.user_name} deleted')
                    emp_details_db = EmployeeDetails.query.filter(
                        EmployeeDetails.employee_login_id == empid,
                    ).first()
                    if emp_details_db is not None:
                        email_send_ref = EmailSend(
                            thread_name="Employee Deletion",
                            email=emp_details_db.emailID,
                            subject=f"{server_name} | Employee Account Deleted",
                            body=f"""
                            Hi {emp_details_db.first_name},
                            
                            Your employee access for user {emp_details_db.emailID}
                            has been revoked.
                            Thanks for being a valued employee.
    
                            Thanks and Regards,
                            Bot.
                            """
                        )
                        email_send_ref.start()

                    db.session.delete(emp_login_db)
                    db.session.commit()

                    cookies = [
                        [AUTH_COOKIE_ADMIN, req_cookies[AUTH_COOKIE_ADMIN], EXPIRE_1_WEEK],
                    ]
                    redirect = _redirect(destination='adminUserAccess', cookies=cookies)
                    return redirect, 302
            else:
                # Cookie is wrong
                cookies = [
                    [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='adminSignIn', cookies=cookies)
                return redirect, 302
        else:
            # No Cookie
            cookies = [
                [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='adminSignIn', cookies=cookies)
            return redirect, 302
    else:
        abort(401)


@app.route('/admin/logout', methods=[GET])
def admin_logout():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE_ADMIN])

    if req_method == GET:
        cookies = [
            [AUTH_COOKIE_ADMIN, BLANK, EXPIRE_NOW],
        ]
        redirect = _redirect(destination='adminSignIn', cookies=cookies)
        return redirect, 302
    else:
        abort(401)
