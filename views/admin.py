from base import *


# =============================================

class AdminPage():
    def __init__(self, login_id: str, password: str):
        self.login_id = login_id
        self.password = password


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
        abort(401)


# ==========================================================

def adminWelcome() -> str:
    if request.method == GET:
        page_name = 'admin_welcome.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


# ==========================================================

def adminInventory() -> str:
    if request.method == GET:
        page_name = 'admin_inventory.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


# ==========================================================

def adminPosTerminal() -> str:
    if request.method == GET:
        page_name = 'admin_posTerminal.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


# ==========================================================

def adminMonthlyRevenue() -> str:
    if request.method == GET:
        page_name = 'admin_monthlyRevenue.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


# ==========================================================

def adminOrders() -> str:
    if request.method == GET:
        page_name = 'admin_orders.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


# ==========================================================

def adminreturnItems() -> str:
    if request.method == GET:
        page_name = 'admin_returnItems.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)


# ==========================================================

def adminLogout() -> str:
    if request.method == GET:
        # page_name = 'landingpage.html'
        # path = os.path.join(page_name)
        # return render_template(path)
        # res = make_response("")
        res.set_cookie("auth", "data", 60 * 60 * 24 * 2)
        res.headers['location'] = url_for('adminWelcome')
        return res, 302
    else:
        abort(401)

# ==========================================================
