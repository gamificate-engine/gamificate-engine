from app import stripe, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, login_required
from app.models import Admin, Realm, Reward
from app.realms import bp
import os

STRIPE_SUB_PLAN = os.environ['STRIPE_SUB_PLAN']

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
        items=[{"plan": STRIPE_SUB_PLAN}],
    )
    
    admin = Admin.query.get_or_404(current_user.get_id())

    activate_realms(admin.realms.all())
    free_realm(admin.realms.first())

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

    limit_realm(admin.realms.first())
    deactivate_realms(admin.realms.all())
    admin.premium = 0
    admin.subscription_key = None
    db.session.add(admin)
    db.session.commit()

    flash('You\'ve cancelled your Premium account!')
    return redirect(url_for('realms.realms'))


def limit_realm(realm):
    if(realm):
        users = realm.users.all()
        if len(users) > 250:
            for user in users[250:]:
                user.active = False
    # no need to commit, will be made when commiting admin


def deactivate_realms(realms):
    if len(realms) > 0:
        realms.pop(0)
    for realm in realms:
        print(realm)
        realm.active = False



def free_realm(realm):
    if(realm):
        users = realm.users.all()
        for user in users[250:]:
            user.active = True


def activate_realms(realms):
    for realm in realms:
        print(realm)
        realm.active = True