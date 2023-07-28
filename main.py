# ========================================================
# IMPORTS
import hashlib
import json
import os
from pathlib import Path

from flask import Flask, render_template, abort, request, make_response, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, DateTime
from sqlalchemy.sql import func

# ========================================================
# CONSTANTS

SECRET = "SECRET"
DATABASE = "DATABASE"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"
HOST = "HOST"
PORT = "PORT"
NAME = "NAME"
GET = "GET"
POST = "POST"
DEBUG = True
EXPIRE_NOW = 0
EXPIRE_1_WEEK = 60 * 60 * 24 * 7
BLANK = ''
AUTH_COOKIE = "auth"
# ========================================================

PROJECT_DIR = Path(__file__).resolve().parent

# ========================================================
# DATABASE + APP

try:
    app = Flask(__name__)
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
        app.config['SECRET_KEY'] = data[SECRET]
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

    customer_details = db.relationship('CustomerDetails', backref='customer_login', lazy=True)
    customer_sales = db.relationship('CustomerSales', backref='customer_login', lazy=True)

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

    customer_login_id = db.Column(db.Integer, db.ForeignKey("customer_login.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


class CustomerSales(db.Model):
    __tablename__ = 'customer_sales'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    customer_login_id = db.Column(db.Integer, db.ForeignKey("customer_login.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"SALE ID : {self.id}"


# =========================

# =========================

# =========================

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


@app.route('/customer', methods=[GET])
def customer_landing_page():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE] is None:
            # No user is logged in
            cookies = [
                [AUTH_COOKIE, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='customer_signin', cookies=cookies)
            return redirect, 302
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE],
            ).first()
            if customer_login_db is not None:
                flag_user_exists = True
            else:
                flag_user_exists = False

            if flag_user_exists:
                # Existing Cookie belongs to user in DB
                cookies = [
                    [AUTH_COOKIE, req_cookies[AUTH_COOKIE], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination='customer_OrderPlacement', cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE, BLANK, EXPIRE_NOW],
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
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE] is None:
            # No user is logged in
            page_name = 'customer_loginpage.html'
            path = os.path.join(page_name)
            return render_template(path)
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE],
            ).first()
            if customer_login_db is not None:
                flag_user_exists = True
            else:
                flag_user_exists = False

            if flag_user_exists:
                # Existing Cookie belongs to user in DB
                cookies = [
                    [AUTH_COOKIE, req_cookies[AUTH_COOKIE], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination='customer_OrderPlacement', cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
                return redirect, 302

    elif req_method == POST:
        if req_cookies[AUTH_COOKIE] is None:
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
                flag_user_exists = True
            else:
                flag_user_exists = False

            if flag_user_exists:
                cookies = [
                    ['auth', customer_login_db.user_name, EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination='customer_OrderPlacement', cookies=cookies)
                return redirect, 302
            else:
                flash('Please Provide Correct Information')
                cookies = [
                    ['auth', BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
                return redirect, 302
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE],
            ).first()
            if customer_login_db is not None:
                flag_user_exists = True
            else:
                flag_user_exists = False

            if flag_user_exists:
                # Existing Cookie belongs to user in DB
                cookies = [
                    [AUTH_COOKIE, req_cookies[AUTH_COOKIE], EXPIRE_1_WEEK],
                ]
                redirect = _redirect(destination='customer_OrderPlacement', cookies=cookies)
                return redirect, 302
            else:
                cookies = [
                    [AUTH_COOKIE, BLANK, EXPIRE_NOW],
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
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE] is None:
            # No user logged in
            cookies = [
                [AUTH_COOKIE, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='customer_signin', cookies=cookies)
            return redirect, 302
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE],
            ).first()
            if customer_login_db is not None:
                flag_user_exists = True
            else:
                flag_user_exists = False

            if flag_user_exists:
                # Existing Cookie belongs to user in DB
                page_name = 'customer_OrderPlacement.html'
                path = os.path.join(page_name)
                return render_template(path)
            else:
                cookies = [
                    [AUTH_COOKIE, BLANK, EXPIRE_NOW],
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
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE] is None:
            # No user logged in
            page_name = 'customer_signup.html'
            path = os.path.join(page_name)
            return render_template(path)
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE],
            ).first()
            if customer_login_db is not None:
                flag_user_exists = True
            else:
                flag_user_exists = False

            if flag_user_exists:
                # Existing Cookie belongs to user in DB
                cookies = [
                    [AUTH_COOKIE, req_cookies[AUTH_COOKIE], EXPIRE_1_WEEK],
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
            # User exists -> Redirect to login page
            flag_user_exists = True
        else:
            # User does not exists -> Create New user
            flag_user_exists = False
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

        # Creating Database Entry for New Customer Data <<<<<<<<<<<

        if flag_user_exists:
            # If user exists -> Redirect to Signup Page
            cookies = [
                [AUTH_COOKIE, BLANK, EXPIRE_NOW],
            ]
            flash('Email ID Exists')
            redirect = _redirect(destination='customer_SignUp', cookies=cookies)
            return redirect, 302
        else:
            # If New user -> Redirect to Order Placement Page
            cookies = [
                [AUTH_COOKIE, customer_login_db.user_name, EXPIRE_1_WEEK],
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
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE])

    if req_method == GET:
        if req_cookies[AUTH_COOKIE] is None:
            # No user logged in
            cookies = [
                [AUTH_COOKIE, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='customer_signin', cookies=cookies)
            return redirect, 302
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE],
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
                    [AUTH_COOKIE, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
                return redirect, 302

    elif req_method == POST:
        form_data = request.form
        if req_cookies[AUTH_COOKIE] is None:
            # No user logged in
            cookies = [
                [AUTH_COOKIE, BLANK, EXPIRE_NOW],
            ]
            redirect = _redirect(destination='customer_signin', cookies=cookies)
            return redirect, 302
        else:
            # User already logged in
            customer_login_db = CustomerLogin.query.filter(
                CustomerLogin.user_name == req_cookies[AUTH_COOKIE],
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
                    CustomerLogin.user_name == req_cookies[AUTH_COOKIE],
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
                                    [AUTH_COOKIE, req_cookies[AUTH_COOKIE], EXPIRE_1_WEEK],
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
                            [AUTH_COOKIE, req_cookies[AUTH_COOKIE], EXPIRE_1_WEEK],
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
                            [AUTH_COOKIE, req_cookies[AUTH_COOKIE], EXPIRE_1_WEEK],
                        ]
                        redirect = _redirect(destination='customer_editProfile', cookies=cookies)
                        return redirect, 302

            else:
                cookies = [
                    [AUTH_COOKIE, BLANK, EXPIRE_NOW],
                ]
                redirect = _redirect(destination='customer_signin', cookies=cookies)
                return redirect, 302
    else:
        abort(401)


@app.route('/customer/logout', methods=[GET])
def customerLogout():
    req_method = request.method
    req_cookies = _get_cookies(request.cookies, [AUTH_COOKIE])

    if req_method == GET:
        cookies = [
            [AUTH_COOKIE, BLANK, EXPIRE_NOW],
        ]
        redirect = _redirect(destination='customer_signin', cookies=cookies)
        return redirect, 302
    else:
        abort(401)


# ======================


class EmployeeSignin:
    def __init__(self, login_id: str, password: str):
        self.login_id = login_id.upper()
        self.password = password


@app.route('/employee', methods=[GET, POST])
def employee_signin():
    page_name_2 = 'employee_welcome.html'
    if request.method == GET:
        page_name = 'employee_signin.html'
        try:
            auth = request.cookies.get('auth')
            if auth is not None:
                raise Exception("Cookie Found")
        except Exception as e:
            print(str(e))
            cookies = [
                ['auth', '', 0],
            ]
            redirect = _redirect(destination='employeeWelcome', cookies=cookies)
            return redirect, 302
        else:
            path = os.path.join(page_name)
            return render_template(path)
    elif request.method == POST:
        form_data = request.form
        employee_page_ref = EmployeeSignin(
            login_id=form_data["loginID"],
            password=form_data["password"],
        )
        path = os.path.join(page_name_2)
        # return render_template(path)
        res = make_response()
        res.set_cookie(AUTH_COOKIE, "DATA HERE", 60 * 60 * 24 * 2)
        res.headers['location'] = url_for('employeeWelcome')
        return res, 302
    else:
        abort(401)


@app.route('/employee/welcome', methods=[GET, POST])
def employeeWelcome() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie(AUTH_COOKIE, '', 0)
            res.headers['location'] = url_for('employee_signin')
            return res, 302
        else:
            page_name = 'employee_welcome.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/employee/inventory', methods=[GET, POST])
def employeeInventory() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie(AUTH_COOKIE, '', 0)
            res.headers['location'] = url_for('employee_signin')
            return res, 302
        else:
            page_name = 'employee_inventory.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/employee/posTerminal', methods=[GET, POST])
def employeePosTerminal() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie(AUTH_COOKIE, '', 0)
            res.headers['location'] = url_for('employee_signin')
            return res, 302
        else:
            page_name = 'employee_posTerminal.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/employee/monthlyRevenue', methods=[GET, POST])
def employeeMonthlyRevenue() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie(AUTH_COOKIE, '', 0)
            res.headers['location'] = url_for('employee_signin')
            return res, 302
        else:
            page_name = 'employee_monthlyRevenue.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/employee/orders', methods=[GET, POST])
def employeeOrders() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie(AUTH_COOKIE, '', 0)
            res.headers['location'] = url_for('employee_signin')
            return res, 302
        else:
            page_name = 'employee_orders.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/employee/returnItems', methods=[GET, POST])
def employeereturnItems() -> str:
    if request.method == GET:
        try:
            auth = request.cookies.get('auth')
            if auth is None:
                raise Exception("Cookie not found")
        except Exception as e:
            print(str(e))
            res = make_response()
            res.set_cookie(AUTH_COOKIE, '', 0)
            res.headers['location'] = url_for('employee_signin')
            return res, 302
        else:
            page_name = 'employee_returnItems.html'
            path = os.path.join(page_name)
            return render_template(path)
    else:
        abort(401)


@app.route('/employee/logout', methods=[GET, POST])
def employeeLogout():
    if request.method == GET:
        res = make_response()
        res.set_cookie(AUTH_COOKIE, '', 0)
        res.headers['location'] = url_for('employee_signin')
        return res, 302
    else:
        abort(401)

# ==========================================================
