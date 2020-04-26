from app import db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm, Badge, User
from app.realms.forms import RealmForm, BadgeForm, UserForm
from werkzeug.urls import url_parse
from flask import request
from app.realms import bp
from app.realms.email import send_api_key_email
from binascii import hexlify # generate API Key
import os

@bp.route('/realms/') #/<admin_id>/')
@login_required
def realms():#admin_id):
    admin = Admin.query.get_or_404(current_user.get_id())

    return render_template('realms/index.html', admin=admin, realms=admin.realms.all())#, admin=admin, realms=realms)



@bp.route('/realms/new', methods=['GET', 'POST'])
@login_required
def new_realm():
    admin = Admin.query.get_or_404(current_user.get_id())

    form = RealmForm()
    
    if form.validate_on_submit():
        api_key = hexlify(os.urandom(16)).decode()

        realm = Realm(name = form.name.data, admin_id = current_user.get_id())
        realm.set_api_key(api_key)

        send_api_key_email(admin, api_key, realm)

        db.session.add(realm)
        db.session.commit()

        flash('Congratulations, you created a new realm! Realm\'s API Key was sent to your email!')
        return redirect(url_for('realms.realms'))
    
    return render_template('realms/new.html', admin=admin, form=form)



def calculate_avg_completed(realm):
    return 25 # TODO: implement logic

@bp.route('/realms/<id>', methods=['GET', 'POST'])
@login_required
def show_realm(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    total_users = realm.users.count()
    total_badges = realm.badges.count()
    total_rewards = realm.rewards.count()
    avg_completed = calculate_avg_completed(realm)

    return render_template('realms/show.html', realm=realm, admin=admin, total_users=total_users, total_badges=total_badges, avg_completed=avg_completed, total_rewards=total_rewards)


@bp.route('/realms/<id>/api_key')
@login_required
def new_api_key(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    api_key = hexlify(os.urandom(16)).decode()

    realm.set_api_key(api_key)

    send_api_key_email(admin, api_key, realm)

    db.session.add(realm)
    db.session.commit()

    flash('Your new Realm\'s API Key was sent to your email!')
    return redirect(url_for('realms.show_realm', id=id))

# TODO: edit
@bp.route('/realms/<id>/badges')
@login_required
def badges(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    return render_template('realms/badges/index.html', realm=realm, admin=admin, badges=realm.badges.all())


@bp.route('/realms/<int:id>/badges/new', methods=['GET', 'POST'])
@login_required
def new_badge(id):
    realm = Realm.query.get_or_404(id)

    admin = Admin.query.get_or_404(current_user.get_id())

    form = BadgeForm(realm)

    if form.validate_on_submit():
        badge = Badge(name=form.name.data, xp=form.xp.data, required=form.required.data)

        realm.badges.append(badge)

        # db.session.add(badge)
        db.session.commit()

        flash('Congratulations, you created a new badge!')
        return redirect(url_for('realms.badges', id = id))

    return render_template('realms/badges/new.html', admin = admin, realm = realm, form = form)


@bp.route('/realms/<int:id>/users')
@login_required
def users(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    return render_template('realms/users/index.html', realm=realm, admin=admin, users=realm.users.all())

    # TODO: new e edit

@bp.route('realms/<int:id>/users/new', methods=['GET', 'POST'])
@login_required
def new_user(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    form = UserForm(realm)

    if form.validate_on_submit():
        infoUser = {'username' : form.username.data, 'email': form.mail.data}
        user = User()

        user.new_user(infoUser)

        realm.users.append(user)

        # db.session.add(user)
        db.session.commit()

        flash('Congratulations, you created a new user!')
        return redirect(url_for('realms.users', id = id))

    return render_template('realms/users/new.html', admin = admin, realm = realm, form = form)
