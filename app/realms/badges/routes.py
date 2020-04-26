from app import db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm, Badge

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
