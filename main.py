from flask import Flask, render_template, abort, request
import os
from pathlib import Path
# from flask_sqlalchemy import SQLAlchemy


PROJECT_DIR = Path(__file__).resolve().parent
POST = "POST"
GET = "GET"
app = Flask(__name__)

# SqlAlchemy Database Configuration With Mysql
DB_CON = "mysql://root:password:Brezza0585!@127.0.0.1:3306/Lodha_Chemist"
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CON
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

@app.route('/', methods = [GET])
def landingPage() -> str:
    page_name = 'landingpage.html'
    path = os.path.join(page_name)
    return render_template(path)

# ==========================================================

class AdminPage():
    def __init__(self, loginID: str, password: str):
        self.login_id = loginID
        self.password = password

@app.route('/admin', methods = [POST, GET])
def admin_page() -> str:
    page_name_1 = 'admin_signin.html'
    page_name_2 = 'admin_welcome.html'
    if request.method == GET:
        path = os.path.join(page_name_1)
        return render_template(path)
    elif request.method == POST:
        form_data = request.form
        admin_page_ref = AdminPage(
                            loginID=form_data["loginID"],
                            password=form_data["password"],
                        )
        path = os.path.join(page_name_2)
        return render_template(path)
    else:
        abort(404)

# ==========================================================

@app.route('/admin/welcome', methods = [GET])
def adminWelcome() -> str:
    page_name = 'admin_welcome.html'
    path = os.path.join(page_name)
    return render_template(path)

# ==========================================================

@app.route('/admin/inventory', methods = [GET])
def adminInventory() -> str:
    page_name = 'admin_inventory.html'
    path = os.path.join(page_name)
    return render_template(path)

# ==========================================================

@app.route('/admin/posTerminal', methods = [GET])
def adminPosTerminal() -> str:
    page_name = 'admin_posTerminal.html'
    path = os.path.join(page_name)
    return render_template(path)

# ==========================================================

@app.route('/admin/monthlyRevenue', methods = [GET])
def adminMonthlyRevenue() -> str:
    page_name = 'admin_monthlyRevenue.html'
    path = os.path.join(page_name)
    return render_template(path)

# ==========================================================

@app.route('/admin/orders', methods = [GET])
def adminOrders() -> str:
    page_name = 'admin_orders.html'
    path = os.path.join(page_name)
    return render_template(path)

# ==========================================================
@app.route('/admin/returnItems', methods = [GET])
def adminreturnItems() -> str:
    page_name = 'admin_returnItems.html'
    path = os.path.join(page_name)
    return render_template(path)
# ==========================================================

@app.route('/admin/logout', methods = [GET])
def adminLogout() -> str:
    # Clear cookies and session data before rerouting
    page_name = 'landingpage.html'
    path = os.path.join(page_name)
    return render_template(path)

# ==========================================================

class CustomerPage():
    def __init__(self, loginID: str, password: str):
        self.login_id = loginID
        self.password = password

@app.route('/customer', methods = ['POST', 'GET'])
def customer_page() -> str:
    page_name_1 = 'customer_loginpage.html'
    page_name_2 = 'customer_OrderPlacement.html'
    if request.method == GET:
        path = os.path.join(page_name_1)
        return render_template(path)
    elif request.method == POST:
        form_data = request.form
        admin_page_ref = AdminPage(
            loginID=form_data["loginID"],
            password=form_data["password"],
        )
        path = os.path.join(page_name_2)
        return render_template(path)
    else:
        abort(404)

# ==========================================================

@app.route('/customer/SignUp', methods = ['POST', 'GET'])
def customer_SignUpp() -> str:
    page_name = 'customer_signup.html'
    path = os.path.join(page_name)
    return render_template(path)

# ==========================================================

@app.route('/customer/changeProfile', methods = ['POST', 'GET'])
def customer_changeProfile() -> str:
    page_name = 'customer_editProfile.html'
    path = os.path.join(page_name)
    return render_template(path)
# ==========================================================


if __name__ == '__main__':
    # Create all tables in DB
    # db.create_all()
    # Run Engine
    app.run(host='127.0.0.1', port=8000, debug=True)
