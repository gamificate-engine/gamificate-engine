from app.api import bp
from flask import jsonify, request
from app.models import Realm, Reward, UserRewards
from app.api.errors import bad_request, error_response
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

# GET REWARD WITH GIVEN ID
@bp.route('/rewards/<int:id>', methods=['GET'])
@jwt_required
@swag_from('../docs/rewards/get.yaml')
def get_reward(id):
    id_realm = get_jwt_identity()

    reward = Reward.query.get(id)
    if not reward:
        return error_response(404, "Reward with given ID does not exist.")

    if reward.id_realm != id_realm:
        return error_response(401, "Reward does not belong to your Realm.")

    return jsonify(reward.to_dict())

# GET ALL REWARDS
@bp.route('/rewards', methods=['GET'])
@jwt_required
@swag_from('../docs/rewards/get_all.yaml')
def get_rewards():
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")
    res = []
    rewards = realm.rewards.all()
    for reward in rewards:
        res.append(reward.to_dict())
    return jsonify({'rewards': res})

# GET REWARD'S REDEEMS
@bp.route('/rewards/<int:id>/redeems', methods=['GET'])
@jwt_required
@swag_from('../docs/rewards/get_redeems.yaml')
def get_reward_redeems(id):
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")
    
    reward = Reward.query.get(id)
    if not reward:
        return error_response(404, "Reward with given ID does not exist.")

    res = []
    reward_redeems = UserRewards.query.filter_by(id_reward=id)
    for row in reward_redeems:
        res.append({
            'id_user': row.id_user,
            'redeem_date': row.redeem_date
        })
    return jsonify({'reward_redeems': res})

# GET ALL REWARDS' REDEEMS
# TODO: NEEDS TESTING !!!
@bp.route('/rewards/redeems', methods=['GET'])
@jwt_required
@swag_from('../docs/rewards/get_all_redeems.yaml')
def get_all_reward_redeems():
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm does not exist.")
    res = []
    rewards = realm.rewards.all()
    for reward in rewards:
        id = reward.id_reward
        reward_redeems = UserRewards.query.filter_by(id_reward=id)
        redeems = []
        for row in reward_redeems:
            redeems.append({
                'id_user': row.id_user,
                'redeem_date': row.redeem_date
            })
        reward_dict = {
            'id_reward': id,
            'redeems': redeems
        }
        res.append(reward_dict)

    return jsonify({'rewards': res})