from app import db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm, Reward
from app.realms import bp
from app.realms.rewards.forms import RewardForm

@bp.route('/realms/<id>/rewards')
@login_required
@check_owernership
def rewards(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    return render_template('realms/rewards/index.html', realm=realm, admin=admin, rewards=realm.rewards.all())


@bp.route('/realms/<int:id>/rewards/new', methods=['GET', 'POST'])
@login_required
@check_owernership
def new_reward(id):
    realm = Realm.query.get_or_404(id)

    admin = Admin.query.get_or_404(current_user.get_id())

    form = RewardForm()
    form.realm = realm 

    if form.validate_on_submit():
        reward = Reward(name=form.name.data, desc=form.desc.data)
        
        realm.rewards.append(reward)       
        db.session.add(reward)
        db.session.commit()

        flash('Congratulations, you\'ve created a new reward!')
        return redirect(url_for('realms.rewards', id = id))

    return render_template('realms/rewards/new.html', admin = admin, realm = realm, form = form)

    # TODO: edit and show