from base import *


def landingPage() -> str:
    if request.method == GET:
        page_name = 'landingpage.html'
        path = os.path.join(page_name)
        return render_template(path)
    else:
        abort(401)