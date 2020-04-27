from flask import abort
from flask_login import current_user
from app.models import Realm
from functools import wraps

def check_owernership(f):
    @wraps(f)
    def wrapper(id):
        realm = Realm.query.get_or_404(id)
        
        if realm.id_admin != current_user.get_id():
            abort(403)

        return f(id)

    return wrapper

