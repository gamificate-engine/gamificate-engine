

# TODO : edit
# TODO : rewards
from flask import flash, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from app import db
from app.badges import bp
from app.models import Realm, Admin, Badge
from app.badges.forms import BadgeForm


@bp.route('/badges/<id>', methods=['GET', 'POST'])
@login_required
def new_badge(id):
    realm = Realm.query.filter_by(id_realm=id).first()
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

    form = BadgeForm()

    if form.validate_on_submit():
        badge = Badge(name=form.name.data, xp=form.xp.data, required=form.required.data, id_realm=id)

        db.session.add(badge)
        db.session.commit()

        flash('Congratulations, you created a new badge!')
        return redirect(url_for('realms.badges', id = id))

    return render_template('realms/badges/new.html', admin = admin, realm = realm, form = form)
