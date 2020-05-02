from app import db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm, User
from app.realms import bp
from app.realms.decorators import check_ownership

# ADAPTED FROM API FUNCS:
def get_leaderboard(id, attr):
    realm = Realm.query.get_or_404(id)
    res = []
    users = realm.users.all()
    # sort in desc order
    users = sorted(users, key=lambda user: getattr(user, attr), reverse=True)
    for index, user in enumerate(users, start=1):
        res.append(user.rank_to_dict(index))
    return res

@bp.route('/realms/<int:id>/leaderboards')
@login_required
@check_ownership
def leaderboards(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    return render_template('realms/leaderboards/index.html', realm=realm, admin=admin, 
        leaderboard_level=get_leaderboard(id,'level'), 
        leaderboard_badges=get_leaderboard(id,'total_badges'), 
        leaderboard_xp=get_leaderboard(id,'total_xp'))