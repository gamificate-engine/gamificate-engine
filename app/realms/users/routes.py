from app import db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm, User
from app.realms import bp
from app.realms.users.forms import UserForm


@bp.route('/realms/<int:id>/users')
@login_required
def users(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    return render_template('realms/users/index.html', realm=realm, admin=admin, users=realm.users.all())


@bp.route('/realms/<int:id>/users/new', methods=['GET', 'POST'])
@login_required
def new_user(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    form = UserForm()
    form.realm = realm

    if form.validate_on_submit():
        infoUser = {'username' : form.username.data, 'email': form.email.data}
        user = User()
        user.new_user(infoUser)

        realm.users.append(user)

        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you\'ve created a new user!')
        return redirect(url_for('realms.users', id = id))

    return render_template('realms/users/new.html', admin = admin, realm = realm, form = form)

    # TODO: edit and show