from app.api import bp
from flask import jsonify, request
from app.models import Realm, User
from app.api.errors import bad_request, error_response
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity

# LEADERBOARD - LEVEL
@bp.route('/leaderboards/level', methods=['GET'])
@jwt_required
def get_level_leaderboard():
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm with given ID does not exist.")

    res = []

    users = realm.users.all()
    # sort in desc order
    users = sorted(users, key=lambda user: user.level, reverse=True)

    for index, user in enumerate(users, start=1):
        res.append(user.rank_to_dict(index, 'level'))

    return jsonify({'leaderboard': res})

# LEADERBOARD - TOTAL XP
@bp.route('/leaderboards/total_xp', methods=['GET'])
@jwt_required
def get_total_xp_leaderboard():
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm with given ID does not exist.")

    res = []

    users = realm.users.all()
    # sort in desc order
    users = sorted(users, key=lambda user: user.total_xp, reverse=True)

    for index, user in enumerate(users, start=1):
        res.append(user.rank_to_dict(index, 'total_xp'))

    return jsonify({'leaderboard': res})

# LEADERBOARD - TOTAL BADGES
@bp.route('/leaderboards/total_badges', methods=['GET'])
@jwt_required
def get_total_badges_leaderboard():
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm with given ID does not exist.")

    res = []

    users = realm.users.all()
    # sort in desc order
    users = sorted(users, key=lambda user: user.total_badges, reverse=True)

    for index, user in enumerate(users, start=1):
        res.append(user.rank_to_dict(index, 'total_badges'))

    return jsonify({'leaderboard': res})