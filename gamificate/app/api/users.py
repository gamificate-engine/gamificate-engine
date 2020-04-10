from app.api import bp
from flask import jsonify, request
from app.models import *
from app.api.errors import bad_request
from app import db

@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/users', methods=['GET'])
def get_users():
    res = []
    users = User.query.all()
    for user in users:
        res.append(user.to_dict())
    return jsonify( {'users': res} )

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data:
        return bad_request('must include username')

    if 'email' not in data:
        return bad_request('must include email')

    if 'realm_id' not in data:
        return bad_request('must include realm id')

    if User.query.filter_by(email=data['username']).first():
        return bad_request('please use a different username')

    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')

    user = User()
    user.new_user(data)

    db.session.add(user)
    db.session.commit()

    response = jsonify(user.to_dict())
    response.status_code = 201

    return response

@bp.route('/users/<int:id>', methods=['PUT'])
def update_user_info(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}

    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')

    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    
    user.from_dict(data)
    db.session.commit()

    return jsonify(user.to_dict())

@bp.route('/users/<int:id>/badge', methods=['PUT'])
def add_badge_progress(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}

    if 'id_badge' not in data:
        return bad_request('must include id_badge')

    if 'progress' not in data:
        return bad_request('must include progress')

    id_badge = int(data['id_badge'])
    progress = int(data['progress'])

    badge = Badge.query.get_or_404(id_badge)

    badge_progress = UserBadges.query.get((id,id_badge))

    if badge_progress is not None:
        badge_progress.update_progress(progress)
    else:
        badge_progress = UserBadges(progress=0,finished=False)
        badge_progress.badge = badge
        user.badges.append(badge_progress)

        badge_progress.update_progress(progress)

    db.session.commit()

    return jsonify(badge_progress.to_dict())

@bp.route('/users/<int:id>/badge', methods=['GET'])
def get_badge_progress(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}

    if 'id_badge' not in data:
        return bad_request('must include id_badge')

    id_badge = int(data['id_badge'])
    badge = Badge.query.get_or_404(id_badge)

    badge_progress = UserBadges.query.get_or_404((id,id_badge))

    return jsonify(badge_progress.to_dict())

@bp.route('/users/<int:id>/badges/all', methods=['GET'])
def get_user_badges(id):
    user = User.query.get_or_404(id)

    res = []
    badges = user.badges
    for badge in badges:
        res.append(badge.to_dict())
    return jsonify( {'user_badges': res} )

@bp.route('/users/<int:id>/badges/finished', methods=['GET'])
def get_user_finished_badges(id):
    user = User.query.get_or_404(id)

    res = []
    badges = user.badges
    for badge in badges:
        if badge.finished:
            res.append(badge.to_dict())
    return jsonify( {'user_badges_finished': res} )
    