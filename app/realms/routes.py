from app import db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm, User, Badge
from app.realms.forms import RealmForm, SettingsForm, ResetPasswordForm, DeleteForm, RealmNameForm
from werkzeug.urls import url_parse
from flask import request
from app.realms import bp
from app.realms.email import send_api_key_email
from binascii import hexlify # generate API Key
import os
from app.realms.decorators import check_ownership, check_active
import random
from app.realms.graphs import calculate_avg_completed, generate_colors, get_levels, get_badge_completion

@bp.route('/realms/')
@login_required
def realms():
    admin = Admin.query.get_or_404(current_user.get_id())

    return render_template('realms/index.html', admin=admin, realms=admin.realms.all())



@bp.route('/realms/new', methods=['GET', 'POST'])
@login_required
def new_realm():
    admin = Admin.query.get_or_404(current_user.get_id())

    form = RealmForm()
    
    if form.validate_on_submit():
        api_key = hexlify(os.urandom(16)).decode()

        realm = Realm(name = form.name.data, description = form.description.data, a = form.a.data, b = form.b.data, id_admin = current_user.get_id())
        realm.set_api_key(api_key)

        send_api_key_email(admin, api_key, realm)

        db.session.add(realm)
        db.session.commit()

        flash('Congratulations, you created a new realm! Realm\'s API Key was sent to your email!')
        return redirect(url_for('realms.realms'))
    
    return render_template('realms/new.html', admin=admin, form=form)


@bp.route('/realms/<int:id>')
@login_required
@check_ownership
@check_active
def show_realm(id):
    realm = Realm.query.filter_by(id_realm=id).first_or_404()
    admin = Admin.query.get_or_404(current_user.get_id())

    total_users = realm.users.count()
    total_badges = realm.badges.count()
    total_rewards = realm.rewards.count()
    avg_completed = calculate_avg_completed(realm)

    users_by_level = get_levels(realm)
    badges_completed = get_badge_completion(realm)

    form_delete = DeleteForm()
    form_name = RealmNameForm()

    return render_template('realms/show.html', realm=realm, admin=admin, total_users=total_users, total_badges=total_badges, 
                            avg_completed=avg_completed, total_rewards=total_rewards, form_delete=form_delete, form_name=form_name,
                            users_by_level=users_by_level, badges_completed=badges_completed)


@bp.route('/realms/<int:id>/api_key')
@login_required
@check_ownership
@check_active
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


@bp.route('/realms/<int:id>/edit', methods=['POST'])
@login_required
@check_ownership
@check_active
def change_realm_name(id):
    realm = Realm.query.get_or_404(id)
    form = RealmNameForm(request.form)
    
    if form.validate_on_submit():
        realm.name = form.name.data
        
        db.session.add(realm)
        db.session.commit()

        flash('Realm\'s name successfully updated.')
    else:
        flash('Realm\'s name not updated because you have a duplicate name.')

    return redirect(url_for('realms.show_realm', id=id))


@bp.route('/realms/<int:id>/delete', methods=['POST'])
@login_required
@check_ownership
@check_active
def delete_realm(id):
    realm = Realm.query.get_or_404(id)
    form = DeleteForm(request.form)

    if form.validate_on_submit():
        db.session.delete(realm)
        db.session.commit()

        flash('Realm successfully deleted.')
        return redirect(url_for('realms.realms'))

    flash('Realm not deleted because passwords didn\'t match.')
    return redirect(url_for('realms.show_realm', id=id))


@bp.route('/realms/settings')
@login_required
def settings():
    admin = Admin.query.get_or_404(current_user.get_id())

    form_settings = SettingsForm()
    form_password = ResetPasswordForm()
    form_delete = DeleteForm()

    return render_template('realms/settings.html', admin=admin, form_settings=form_settings, form_password=form_password, form_delete=form_delete)

@bp.route('/realms/settings/changesettings', methods=['POST'])
@login_required
def change_settings():
    admin = Admin.query.get_or_404(current_user.get_id())

    form_settings = SettingsForm()

    if form_settings.validate_on_submit():
        admin.email = form_settings.email.data
        admin.first_name = form_settings.first_name.data
        admin.last_name = form_settings.last_name.data
        db.session.add(admin)
        db.session.commit()
        flash('Your settings have been successfully updated.')

    return render_template('realms/settings.html', admin=admin, form_settings=form_settings, form_password=ResetPasswordForm(), form_delete=DeleteForm())

@bp.route('/realms/settings/resetpassword', methods=['POST'])
@login_required
def reset_password():
    admin = Admin.query.get_or_404(current_user.get_id())

    form_password = ResetPasswordForm()

    if form_password.validate_on_submit():
        admin.setPassword(form_password.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('Your password has been successfully updated.')
    
    return render_template('realms/settings.html', admin=admin, form_settings=SettingsForm(), form_password=form_password, form_delete=DeleteForm())
    

@bp.route('/realms/settings/delete', methods=['POST'])
@login_required
def delete():
    admin = Admin.query.get_or_404(current_user.get_id())
    
    form_delete = DeleteForm()

    if form_delete.validate_on_submit():
        db.session.delete(admin)
        db.session.commit()

        logout_user()
        
        return redirect(url_for('main.index'))

    return render_template('realms/settings.html', admin=admin, form_settings=SettingsForm(), form_password=ResetPasswordForm(), form_delete=form_delete)

