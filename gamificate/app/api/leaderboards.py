from app.api import bp
from flask import jsonify, request
from app.models import *
from app.api.errors import bad_request, error_response
from app import db

# LEADERBOARD - LEVEL
@bp.route('/leaderboards/<int:id>/level', methods=['GET'])
def get_level_leaderboard(id):
    realm = Realm.query.get(id)
    if not realm:
        return error_response(404, "Realm with given ID does not exist.")

    res = []

    users = User.query.filter(User.id_realm == id)
    # sort in desc order
    users = sorted(users, key=lambda user: user.level, reverse=True)

    for index, user in enumerate(users, start=1):
        res.append(user.rank_to_dict(index, 'level'))

    return jsonify({'leaderboard': res})

# LEADERBOARD - TOTAL XP
@bp.route('/leaderboards/<int:id>/total_xp', methods=['GET'])
def get_total_xp_leaderboard(id):
    realm = Realm.query.get(id)
    if not realm:
        return error_response(404, "Realm with given ID does not exist.")

    res = []

    users = User.query.filter(User.id_realm == id)
    # sort in desc order
    users = sorted(users, key=lambda user: user.total_xp, reverse=True)

    for index, user in enumerate(users, start=1):
        res.append(user.rank_to_dict(index, 'total_xp'))

    return jsonify({'leaderboard': res})

# LEADERBOARD - TOTAL BADGES
@bp.route('/leaderboards/<int:id>/total_badges', methods=['GET'])
def get_total_badges_leaderboard(id):
    realm = Realm.query.get(id)
    if not realm:
        return error_response(404, "Realm with given ID does not exist.")

    res = []

    users = User.query.filter(User.id_realm == id)
    # sort in desc order
    users = sorted(users, key=lambda user: user.total_badges, reverse=True)

    for index, user in enumerate(users, start=1):
        res.append(user.rank_to_dict(index, 'total_badges'))

    return jsonify({'leaderboard': res})