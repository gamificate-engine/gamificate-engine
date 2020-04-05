from app import db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm
from app.realms.forms import RealmForm
from werkzeug.urls import url_parse
from flask import request
from app.realms import bp


@bp.route('/realms/') #/<admin_id>/')
@login_required
def realms():#admin_id):
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

    return render_template('realms/index.html', admin=admin, realms=admin.realms.all())#, admin=admin, realms=realms)



@bp.route('/realms/new', methods=['GET', 'POST'])
@login_required
def new_realm():
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

    form = RealmForm()
    
    if form.validate_on_submit():
        realm = Realm(name = form.name.data, admin_id = current_user.get_id())

        db.session.add(realm)
        db.session.commit()

        flash('Congratulations, you created a new realm!')
        return redirect(url_for('realms.realms'))
    
    return render_template('realms/new.html', admin=admin, form=form)


@bp.route('/realms/<id>', methods=['GET', 'POST'])
@login_required
def show_realm(id):
    realm = Realm.query.filter_by(id_realm=id).first_or_404()
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

    
    return render_template('realms/show.html', realm=realm, admin=admin)


@bp.route('/realms/<id>/badges')
@login_required
def badges(id):
    realm = Realm.query.filter_by(id_realm=id).first_or_404()
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

    return render_template('realms/badges/index.html', realm=realm, admin=admin, badges=realm.badges.all())


