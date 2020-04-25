from app.api import bp
from flask import jsonify, request
from app.models import Realm, User, Badge, Reward, UserBadges, UserRewards
from app.api.errors import bad_request, error_response
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

# GET USER WITH GIVEN ID
@bp.route('/users/<int:id>', methods=['GET'])
@jwt_required
@swag_from('../docs/users/get.yaml')
def get_user(id):
    id_realm = get_jwt_identity()

    user = User.query.get(id)
    if not user:
        return error_response(404, "User with given ID does not exist.")

    if user.id_realm != id_realm:
        return error_response(401, "User does not belong to your Realm.")

    return jsonify(user.to_dict())

# GET ALL USERS
@bp.route('/users', methods=['GET'])
@jwt_required
@swag_from('../docs/users/get_all.yaml')
def get_users():
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")
    res = []
    users = realm.users.all()
    for user in users:
        res.append(user.to_dict())
    return jsonify({'users': res})

# CREATE NEW USER
@bp.route('/users', methods=['POST'])
@jwt_required
@swag_from('../docs/users/create.yaml')
def create_user():
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")

    admin = Admin.query.get(realm.id_admin)
    if not admin:
        return error_response(404, "Admin does not exist.")
    
    if not admin.premium:
        if realm.users.count() >= 25:
            return error_response(403, "You have reached the max number of users. To add more, please upgrade your free plan to Premium.")

    data = request.get_json() or {}
    if 'username' not in data:
        return bad_request('must include username')

    if 'email' not in data:
        return bad_request('must include email')

    users = realm.users.all()

    if [u.username for u in users if u.username == data['username']]:
        return bad_request('please use a different username')

    if [u.email for u in users if u.email == data['email']]:
        return bad_request('please use a different email address')

    user = User()
    user.new_user(data)

    realm.users.append(user)

    # db.session.add(user)
    db.session.commit()

    response = jsonify(user.to_dict())
    response.status_code = 201

    return response

# UPDATE USER
@bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required
@swag_from('../docs/users/update.yaml')
def update_user_info(id):
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")

    user = User.query.get(id)
    if not user:
        return error_response(404, "User with given ID does not exist.")

    if user.id_realm != id_realm:
        return error_response(401, "User does not belong to your Realm.")

    data = request.get_json() or {}

    users = realm.users.all()

    if 'username' in data and data['username'] != user.username and \
            [u.username for u in users if u.username == data['username']]:
        return bad_request('Please use a different username.')

    if 'email' in data and data['email'] != user.email and \
            [u.email for u in users if u.email == data['email']]:
        return bad_request('Please use a different email address.')

    user.from_dict(data)
    db.session.commit()

    return jsonify(user.to_dict())

# UPDATE USER WITH BADGE PROGRESS
@bp.route('/users/<int:id>/badges', methods=['PUT'])
@jwt_required
@swag_from('../docs/users/badge.yaml')
def add_badge_progress(id):
    id_realm = get_jwt_identity()

    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")

    user = User.query.get(id)
    if not user:
        return error_response(404, "User with given ID does not exist.")
    if user.id_realm != id_realm:
        return error_response(401, "User does not belong to your Realm.")

    # To check if the user leveled up
    level = user.level

    data = request.get_json() or {}

    if 'id_badge' not in data:
        return bad_request('must include id_badge')

    if 'progress' not in data:
        return bad_request('must include progress')

    id_badge = int(data['id_badge'])
    progress = int(data['progress'])

    badge = Badge.query.get(id_badge)
    if not badge:
        return error_response(404, "Badge with given ID does not exist.")
    if badge.id_realm != id_realm:
        return error_response(401, "Badge does not belong to your Realm.")

    badge_progress = UserBadges.query.get((id, id_badge))

    if badge_progress is not None:
        if badge_progress.finished:
            return error_response(403, "Badge already finished.")
        badge_progress.update_progress(progress, badge, user, realm)
    else:
        badge_progress = UserBadges(progress=0, finished=False)
        badge_progress.badge = badge
        user.badges.append(badge_progress)

        badge_progress.update_progress(progress, badge, user, realm)
    
    res = badge_progress.to_dict()

    if user.level > level:
        res['level_up'] = user.level

    db.session.commit()

    return jsonify(res)

# GET GIVEN BAGDE PROGRESS
@bp.route('/users/<int:id>/badges', methods=['GET'])
@jwt_required
@swag_from('../docs/users/get_badge.yaml')
def get_badge_progress(id):
    id_realm = get_jwt_identity()

    user = User.query.get(id)
    if not user:
        return error_response(404, "User with given ID does not exist.")
    if user.id_realm != id_realm:
        return error_response(401, "User does not belong to your Realm.")

    data = request.get_json() or {}

    if 'id_badge' not in data:
        return bad_request('must include id_badge')

    id_badge = int(data['id_badge'])
    badge = Badge.query.get(id_badge)

    if not badge:
        return error_response(404, "Badge with given ID does not exist.")

    if badge.id_realm != id_realm:
        return error_response(401, "Badge does not belong to your Realm.")

    badge_progress = UserBadges.query.get((id, id_badge))
    if not badge_progress:
        return error_response(404, "User has no progress on that Badge.")

    return jsonify(badge_progress.to_dict())

# GET ALL USER BADGES (FINISHED AND NOT FINISHED)
@bp.route('/users/<int:id>/badges/all', methods=['GET'])
@jwt_required
@swag_from('../docs/users/get_badges.yaml')
def get_user_badges(id):
    id_realm = get_jwt_identity()

    user = User.query.get(id)

    if not user:
        return error_response(404, "User with given ID does not exist.")
    if user.id_realm != id_realm:
        return error_response(401, "User does not belong to your Realm.")

    res = []
    badges = user.badges.all()
    for badge in badges:
        res.append(badge.to_dict())
    return jsonify({'user_badges': res})

# GET ALL FINISHED USER BADGES
@bp.route('/users/<int:id>/badges/finished', methods=['GET'])
@jwt_required
@swag_from('../docs/users/get_finished.yaml')
def get_user_finished_badges(id):
    id_realm = get_jwt_identity()

    user = User.query.get(id)

    if not user:
        return error_response(404, "User with given ID does not exist.")
    if user.id_realm != id_realm:
        return error_response(401, "User does not belong to your Realm.")

    res = []
    badges = user.badges.all()
    for badge in badges:
        if badge.finished:
            res.append(badge.to_dict())
    return jsonify({'user_badges_finished': res})

# REDEEM REWARD WITH GIVEN ID
@bp.route('/users/<int:id>/rewards', methods=['POST'])
@jwt_required
@swag_from('../docs/users/redeem.yaml')
def redeem_reward(id):
    id_realm = get_jwt_identity()

    user = User.query.get(id)

    if not user:
        return error_response(404, "User with given ID does not exist.")
    if user.id_realm != id_realm:
        return error_response(401, "User does not belong to your Realm.")

    data = request.get_json() or {}

    if 'id_reward' not in data:
        return bad_request('must include id_reward')

    id_reward = int(data['id_reward'])

    reward = Reward.query.get(id_reward)
    if not reward:
        return error_response(404, "Reward with given ID does not exist.")
    if reward.id_realm != id_realm:
        return error_response(401, "Reward does not belong to your Realm.")

    user_reward = UserRewards.query.get((id, id_reward))
    if user_reward:
        return error_response(403, "Reward already redeemed.")

    user_reward = UserRewards()
    user_reward.redeem(reward)

    user.rewards.append(user_reward)

    db.session.commit()

    response = jsonify(user_reward.to_dict())
    response.status_code = 201
    return response

# GET ALL USER REWARDS
@bp.route('/users/<int:id>/rewards', methods=['GET'])
@jwt_required
@swag_from('../docs/users/rewards.yaml')
def get_user_rewards(id):
    id_realm = get_jwt_identity()

    user = User.query.get(id)

    if not user:
        return error_response(404, "User with given ID does not exist.")
    if user.id_realm != id_realm:
        return error_response(401, "User does not belong to your Realm.")

    res = []
    rewards = user.rewards.all()
    for reward in rewards:
        res.append(reward.to_dict())
    return jsonify({'user_rewards': res})
