from app import stripe, db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm
from app.realms.forms import RealmForm, SettingsForm, ResetPasswordForm, DeleteAccountForm
from werkzeug.urls import url_parse
from flask import request
from app.realms import bp
from app.realms.email import send_api_key_email
from binascii import hexlify # generate API Key
import os
from app.realms.decorators import check_ownership

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



def calculate_avg_completed(realm):
    return 25 # TODO: implement logic

@bp.route('/realms/<id>', methods=['GET', 'POST'])
@login_required
@check_ownership
def show_realm(id):
    realm = Realm.query.filter_by(id_realm=id).first_or_404()
    admin = Admin.query.get_or_404(current_user.get_id())

    total_users = realm.users.count()
    total_badges = realm.badges.count()
    total_rewards = realm.rewards.count()
    avg_completed = calculate_avg_completed(realm)

    return render_template('realms/show.html', realm=realm, admin=admin, total_users=total_users, total_badges=total_badges, avg_completed=avg_completed, total_rewards=total_rewards)


@bp.route('/realms/<id>/api_key')
@login_required
@check_ownership
def new_api_key(id):
    realm = Realm.query.filter_by(id_realm=id).first_or_404()
    admin = Admin.query.get_or_404(current_user.get_id())

    api_key = hexlify(os.urandom(16)).decode()

    realm.set_api_key(api_key)

    send_api_key_email(admin, api_key, realm)

    db.session.add(realm)
    db.session.commit()

    flash('Your new Realm\'s API Key was sent to your email!')
    return redirect(url_for('realms.show_realm', id=id))


@bp.route('/realms/payment', methods=['POST'])
@login_required
def payment():
    customer = stripe.Customer.list(email=request.form['stripeEmail'])
    
    if customer.data:
        customer = customer.data[0]
    else:
        customer = stripe.Customer.create(
            email=request.form['stripeEmail'],
            source=request.form['stripeToken']
        )

    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{"plan": "plan_H7quRNGUfctwNA"}],
    )
    
    admin = Admin.query.get_or_404(current_user.get_id())
    admin.premium = 1
    admin.subscription_key = subscription.id

    db.session.add(admin)
    db.session.commit()

    flash('Congratulations, you now have a Premium account!')
    return redirect(url_for('realms.realms'))


@bp.route('/realms/premium')
@login_required
def premium():
    admin = Admin.query.get_or_404(current_user.get_id())

    return render_template('realms/premium.html', admin=admin, key=stripe.publishable_key)

@bp.route('/realms/cancel')
@login_required
def cancel():
    admin = Admin.query.get_or_404(current_user.get_id())
    stripe.Subscription.delete(admin.subscription_key)

    admin.premium = 0
    admin.subscription_key = None
    db.session.add(admin)
    db.session.commit()

    flash('You\'ve cancelled your Premium account!')
    return redirect(url_for('realms.realms'))


@bp.route('/realms/settings')
@login_required
def settings():
    admin = Admin.query.get_or_404(current_user.get_id())

    form_settings = SettingsForm()
    form_password = ResetPasswordForm()
    form_delete = DeleteAccountForm()

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

    return render_template('realms/settings.html', admin=admin, form_settings=form_settings, form_password=ResetPasswordForm(), form_delete=DeleteAccountForm())

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
    
    return render_template('realms/settings.html', admin=admin, form_settings=SettingsForm(), form_password=form_password, form_delete=DeleteAccountForm())
    

@bp.route('/realms/settings/delete', methods=['POST'])
@login_required
def delete():
    admin = Admin.query.get_or_404(current_user.get_id())
    
    form_delete = DeleteAccountForm()

    if form_delete.validate_on_submit():
        db.session.delete(admin)
        db.session.commit()

        logout_user()
        
        return redirect(url_for('main.index'))

    return render_template('realms/settings.html', admin=admin, form_settings=SettingsForm(), form_password=ResetPasswordForm(), form_delete=form_delete)
