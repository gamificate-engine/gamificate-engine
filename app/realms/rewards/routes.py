from app import db, app
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm, Reward
from app.realms import bp
from app.realms.rewards.forms import RewardForm, EditForm
from app.realms.decorators import check_ownership

@bp.route('/realms/<id>/rewards')
@login_required
@check_ownership
def rewards(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    page = request.args.get('page', 1, type=int)
    pagination = realm.rewards.paginate(page, app.config['REWARDS_PER_PAGE'], True)
    rewards = pagination.items
    next_url = url_for('realms.rewards', id=id, page=pagination.next_num) if pagination.has_next else None
    prev_url = url_for('realms.rewards', id=id, page=pagination.prev_num) if pagination.has_prev else None

    form = EditForm()
    form.realm = realm

    return render_template('realms/rewards/index.html', realm=realm, admin=admin, rewards=rewards,
                           form=form, next_url=next_url, prev_url=prev_url)


@bp.route('/realms/<int:id>/rewards/new', methods=['GET', 'POST'])
@login_required
@check_ownership
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


@bp.route('/realms/<int:id>/rewards/edit', methods=['POST'])
@login_required
@check_ownership
def edit_reward(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    form = EditForm(request.form)
    form.realm = realm

    if form.validate_on_submit():
        reward_id = form.id.data

        infoReward = {'name' : form.name.data, 'description': form.description.data}

        reward = Reward.query.get_or_404(reward_id)

        if reward.id_realm != id:
            return render_template('errors/403.html'), 403
        else:
            reward.from_dict(infoReward)
            db.session.commit()
            flash('Reward edited with success!')
    
    else:
        flash('Something went wrong. Please try again.')

    return redirect(url_for('realms.rewards', id=id))

@bp.route('/realms/<int:id>/rewards/delete', methods=['POST'])
@login_required
@check_ownership
def delete_reward(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    reward_id = request.args.get('reward', None)
    if not reward_id:
        return render_template('errors/404.html'), 404

    reward = Reward.query.get_or_404(reward_id)
    if reward.id_realm != id:
        return render_template('errors/403.html'), 403
    else:
        db.session.delete(reward)
        db.session.commit()
        flash('Reward deleted with success!')

    return redirect(url_for('realms.rewards', id=id))