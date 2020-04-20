from app.api import bp
import os
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity
from flask import request, jsonify
from app.models import Realm
from app.api.errors import bad_request, error_response
from flasgger import swag_from


@bp.route('/auth', methods=['POST'])
@swag_from('../docs/auth/auth.yaml')
def auth():
    data = request.get_json() or {}

    if 'id_realm' not in data:
        return bad_request('Must include id_realm')

    id_realm = int(data['id_realm'])
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm with given ID does not exist.")

    if 'api_key' not in data:
        return bad_request('Must include api_key')

    api_key = data['api_key']
    if not realm.check_api_key(api_key):
        return error_response(401, "Wrong API key")

    # Identity can be any data that is json serializable
    tokens = {
        'refresh_token': create_refresh_token(identity=id_realm),
        'access_token': create_access_token(identity=id_realm)
    }
    
    return jsonify(tokens), 200


@bp.route('/auth/refresh', methods=['POST'])
@jwt_refresh_token_required
@swag_from('../docs/auth/refresh.yaml')
def refresh():
    id_realm = get_jwt_identity()
    realm = Realm.query.get(id_realm)
    if not realm:
        return error_response(404, "Realm with given ID does not exist.")
        
    access_token = create_access_token(identity=id_realm)
    return jsonify(access_token=access_token), 200