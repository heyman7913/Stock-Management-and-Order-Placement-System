from views.customer import *
from views.others import *
from views.admin import *
# =======================================


app.add_url_rule('/', 'landingPage', landingPage)

app.add_url_rule('/admin', 'admin_page', admin_page)
app.add_url_rule('/admin/welcome', 'adminWelcome', adminWelcome)
app.add_url_rule('/admin/inventory', 'adminInventory', adminInventory)
app.add_url_rule('/admin/posTerminal', 'adminPosTerminal', adminPosTerminal)
app.add_url_rule('/admin/monthlyRevenue', 'adminMonthlyRevenue', adminMonthlyRevenue)
app.add_url_rule('/admin/orders', 'adminOrders', adminOrders)
app.add_url_rule('/admin/returnItems', 'adminreturnItems', adminreturnItems)
app.add_url_rule('/admin/logout', 'adminLogout', adminLogout)