from flask import flash, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from app import db
from app.models import Realm, Admin, User
from app.users import bp
from app.users.forms import UserForm


@bp.route('/users/<id>', methods=['GET', 'POST'])
@login_required
def new_user(id):
    realm = Realm.query.filter_by(id_realm=id).first()
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

    form = UserForm()

    if form.validate_on_submit():
        infoUser = {'username' : form.username.data, 'email': form.mail.data, 'id_realm':id}
        user = User()

        user.new_user(infoUser)

        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you created a new user!')
        return redirect(url_for('realms.users', id = id))

    return render_template('realms/users/new.html', admin = admin, realm = realm, form = form)
