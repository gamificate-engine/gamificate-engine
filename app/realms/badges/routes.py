from app import db, app
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm, Badge
from app.realms import bp
from app.realms.badges.forms import BadgeForm, EditForm
from app.realms.decorators import check_ownership

@bp.route('/realms/<id>/badges')
@login_required
@check_ownership
def badges(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    page = request.args.get('page', 1, type=int)
    pagination = realm.badges.paginate(page, app.config['BADGES_PER_PAGE'], True)
    badges = pagination.items
    next_url = url_for('realms.badges', id=id, page=pagination.next_num) if pagination.has_next else None
    prev_url = url_for('realms.badges', id=id, page=pagination.prev_num) if pagination.has_prev else None

    form = EditForm()
    form.realm = realm

    return render_template('realms/badges/index.html', realm=realm, admin=admin,
                           badges=badges, form=form, next_url=next_url, prev_url=prev_url)


@bp.route('/realms/<int:id>/badges/new', methods=['GET', 'POST'])
@login_required
@check_ownership
def new_badge(id):
    realm = Realm.query.get_or_404(id)

    admin = Admin.query.get_or_404(current_user.get_id())

    form = BadgeForm()
    form.realm = realm 
    form.add_rewards()


    if form.validate_on_submit():
        if form.id_reward.data == 0:
            badge = Badge(name=form.name.data, description=form.description.data, xp=form.xp.data, required=form.required.data, image_url=form.image_url.data)
        else:
            badge = Badge(name=form.name.data, description=form.description.data, xp=form.xp.data, required=form.required.data, image_url=form.image_url.data, id_reward=form.id_reward.data)
        
        realm.badges.append(badge)       
        db.session.add(badge)
        db.session.commit()

        flash('Congratulations, you\'ve created a new badge!')
        return redirect(url_for('realms.badges', id = id))

    return render_template('realms/badges/new.html', admin = admin, realm = realm, form = form)


@bp.route('/realms/<int:id>/badges/edit', methods=['POST'])
@login_required
@check_ownership
def edit_badge(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    form = EditForm(request.form)
    form.realm = realm

    if form.validate_on_submit():
        badge_id = form.id.data

        infoBadge = {'name' : form.name.data, 'description': form.description.data, 'image_url': form.image_url.data}

        badge = Badge.query.get_or_404(badge_id)

        if badge.id_realm != id:
            return render_template('errors/403.html'), 403
        else:
            badge.new_or_update(infoBadge)
            db.session.commit()
            flash('Badge edited with success!')
    
    else:
        flash('Something went wrong. Please try again.')

    return redirect(url_for('realms.badges', id=id))

@bp.route('/realms/<int:id>/badges/delete', methods=['POST'])
@login_required
@check_ownership
def delete_badge(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    badge_id = request.args.get('badge', None)
    if not badge_id:
        return render_template('errors/404.html'), 404

    badge = Badge.query.get_or_404(badge_id)
    if badge.id_realm != id:
        return render_template('errors/403.html'), 403
    else:
        db.session.delete(badge)
        db.session.commit()
        flash('Badge deleted with success!')

    return redirect(url_for('realms.badges', id=id))