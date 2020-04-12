from app.api import bp
from flask import jsonify, request
from app.models import *
from app.api.errors import bad_request, error_response
from app import db

# GET BADGE WITH GIVEN ID
@bp.route('/badges/<int:id>', methods=['GET'])
def get_badge(id):
    data = request.get_json() or {}
    if 'id_realm' not in data:
        return bad_request('must include id_realm')

    id_realm = int(data['id_realm'])

    badge = Badge.query.get(id)
    if not badge:
        return error_response(404, "Badge with given ID does not exist.")

    if badge.id_realm != id_realm:
        return error_response(400, "Badge not from the given realm.")

    return jsonify(badge.to_dict())

# GET ALL BADGES
@bp.route('/badges', methods=['GET'])
def get_badges():
    data = request.get_json() or {}

    if 'id_realm' not in data:
        return bad_request('must include id_realm')

    id_realm = int(data['id_realm'])

    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm with given ID does not exist.")

    res = []
    
    badges = Badge.query.filter_by(id_realm=id_realm)

    for badge in badges:
        res.append(badge.to_dict())

    return jsonify( {'badges': res} )

# CREATE NEW BADGE
@bp.route('/badges', methods=['POST'])
def create_badge():
    data = request.get_json() or {}
    if 'name' not in data:
        return bad_request('must include name')

    if 'xp' not in data:
        return bad_request('must include xp')

    if 'required' not in data:
        return bad_request('must include required')

    if 'id_realm' not in data:
        return bad_request('must include id_realm')

    id_realm = int(data['id_realm'])

    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm with given ID does not exist.")


    for badge in realm.badges:
        if badge.name == data['name']:
            return bad_request('please use a different name')

    badge = Badge()
    badge.new_or_update(data)

    realm.badges.append(badge)

    db.session.add(badge)
    db.session.commit()

    response = jsonify(badge.to_dict())
    response.status_code = 201

    return response

# UPDATE BADGE
@bp.route('/badges/<int:id>', methods=['PUT'])
def update_badge(id):
    badge = Badge.query.get(id)
    if not badge:
        return error_response(404, "Badge with given ID does not exist.")

    data = request.get_json() or {}

    if 'name' in data and data['name'] != badge.name and \
            Badge.query.filter_by(name=data['name']).first():
        return bad_request('please use a different name')
    
    badge.new_or_update(data)
    db.session.commit()

    return jsonify(badge.to_dict())