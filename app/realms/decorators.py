from flask import abort
from flask_login import current_user
from app.models import Realm, Admin
from functools import wraps

def check_ownership(f):
    @wraps(f)
    def wrapper(id):
        realm = Realm.query.get_or_404(id)
        
        if realm.id_admin != current_user.get_id():
            abort(403)

        return f(id)

    return wrapper


def check_premium(f):
    @wraps(f)
    def wrapper(id):
        admin = Admin.query.get_or_404(current_user.get_id())
        
        if not admin.premium:
            abort(403)

        return f(id)

    return wrapper


def check_active(f):
    @wraps(f)
    def wrapper(id):
        realm = Realm.query.get_or_404(id)

        if not realm.active:
            abort(403)

        return f(id)

    return wrapper
