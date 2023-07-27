from views.base import *


# ==========================================================

class CustomerPage():
    def __init__(self, login_id: str, password: str):
        self.login_id = login_id
        self.password = password


@app.route('/customer', methods=['POST', 'GET'])
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

@app.route('/customer/SignUp', methods=['POST', 'GET'])
def customer_SignUpp() -> str:
    page_name = 'customer_signup.html'
    path = os.path.join(page_name)
    return render_template(path)


# ==========================================================

@app.route('/customer/changeProfile', methods=['POST', 'GET'])
def customer_changeProfile() -> str:
    page_name = 'customer_editProfile.html'
    path = os.path.join(page_name)
    return render_template(path)
# ==========================================================
