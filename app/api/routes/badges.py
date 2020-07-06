from app.api import bp
from flask import jsonify, request
from app.models import Realm, Badge, UserBadges
from app.api.errors import bad_request, error_response
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from


# GET BADGE WITH GIVEN ID
@bp.route('/badges/<int:id>', methods=['GET'])
@jwt_required
@swag_from('../docs/badges/get.yaml')
def get_badge(id):
    id_realm = get_jwt_identity()

    badge = Badge.query.get(id)
    if not badge:
        return error_response(404, "Badge with given ID does not exist.")

    if badge.id_realm != id_realm:
        return error_response(401, "Badge does not belong to your Realm.")

    return jsonify(badge.to_dict())

# GET ALL BADGES
@bp.route('/badges', methods=['GET'])
@jwt_required
@swag_from('../docs/badges/get_all.yaml')
def get_badges():
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")
    res = []
    badges = realm.badges.all()
    for badge in badges:
        res.append(badge.to_dict())
    return jsonify({'badges': res})

# GET USER'S PROGRESS ON BADGE
@bp.route('/badges/<int:id>/progress', methods=['GET'])
@jwt_required
@swag_from('../docs/badges/get_progress.yaml')
def get_badge_progresses(id):
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")
   
    badge = Badge.query.get(id)
    if not badge:
        return error_response(404, "Badge with given ID does not exist.")

    if badge.id_realm != id_realm:
        return error_response(401, "Badge does not belong to your Realm.")

    finished_list = []
    unfinished_list = []

    with_progress = UserBadges.query.filter_by(id_badge=id)
    for row in with_progress:
        if row.finished:
            finished_list.append(
                {
                    'id_user': row.id_user,
                    'finished_date': row.finished_date
                }
            )
        else:
            unfinished_list.append(
                {
                    'id_user': row.id_user,
                    'progress': row.progress,
                    'required': badge.required
                }
            )

    return jsonify({
        'finished': finished_list,
        'unfinished': unfinished_list
        })

# GET USERS THAT FINISHED THE BADGE
@bp.route('/badges/<int:id>/progress/finished', methods=['GET'])
@jwt_required
@swag_from('../docs/badges/get_finished.yaml')
def get_badge_finished(id):
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")
   
    badge = Badge.query.get(id)
    if not badge:
        return error_response(404, "Badge with given ID does not exist.")

    if badge.id_realm != id_realm:
        return error_response(401, "Badge does not belong to your Realm.")

    res = []

    finished = UserBadges.query.filter_by(id_badge=id, finished=True)
    for row in finished:
        res.append(
            {
                'id_user': row.id_user,
                'finished_date': row.finished_date
            }
        )

    return jsonify({'finished': res})

# GET USERS THAT STARTED THE BADGE
@bp.route('/badges/<int:id>/progress/unfinished', methods=['GET'])
@jwt_required
@swag_from('../docs/badges/get_unfinished.yaml')
def get_badge_unfinished(id):
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")
   
    badge = Badge.query.get(id)
    if not badge:
        return error_response(404, "Badge with given ID does not exist.")

    if badge.id_realm != id_realm:
        return error_response(401, "Badge does not belong to your Realm.")

    res = []

    unfinished = UserBadges.query.filter_by(id_badge=id, finished=False)
    for row in unfinished:
        res.append(
            {
                'id_user': row.id_user,
                'progress': row.progress,
                'required': badge.required
            }
        )

    return jsonify({'unfinished': res})

# GET ALL BADGES PROGRESS
# TODO: NEEDS TESTING !!!
@bp.route('/badges/progress', methods=['GET'])
@jwt_required
@swag_from('../docs/badges/get_all_progress.yaml')
def get_badges_progress():
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")
    res = []
    badges = realm.badges.all()
    for badge in badges:
        id = badge.id_badge
        finished_list = []
        unfinished_list = []
        with_progress = UserBadges.query.filter_by(id_badge=id)
        for row in with_progress:
            if row.finished:
                finished_list.append(
                    {
                        'id_user': row.id_user,
                        'finished_date': row.finished_date
                    }
                )
            else:
                unfinished_list.append(
                    {
                        'id_user': row.id_user,
                        'progress': row.progress,
                        'required': badge.required
                    }
                )
        badge_dict = {
            'id_badge': id,
            'progress': {
                'finished': finished_list,
                'unfinished': unfinished_list
            }
        }
        res.append(badge_dict)

    return jsonify({'badges': res})


