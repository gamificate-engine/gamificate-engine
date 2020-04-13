from app.api import bp
import os
from flask_jwt_extended import create_access_token
from flask import request, jsonify
from app.models import Realm
from app.api.errors import bad_request, error_response


@bp.route('/auth', methods=['POST'])
def auth():
    data = request.get_json() or {}

    if 'id_realm' not in data:
        return bad_request('Must include id_realm')

    id_realm = int(data['id_realm'])
    realm = Realm.query.get(id_realm)

    if 'api_key' not in data:
        return bad_request('Must include api_key')

    api_key = data['api_key']
    if not realm.check_key(api_key):
        return error_response(401, "Wrong API key")

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=id_realm)
    return jsonify(access_token=access_token), 200

def revoke_token():
    pass