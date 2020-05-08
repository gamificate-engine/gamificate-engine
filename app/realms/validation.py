import json
import jsonschema
from jsonschema import validate


user_schema = {
    "type": "object",
    "required": [
        "users"
    ],
    "properties": {
        "users": {
            "$id": "#/properties/users",
            "type": "array",
            "items": {
                "$id": "#/properties/users/items",
                "type": "object",
                "required": [
                    "username",
                    "email"
                ],
                "properties": {
                    "username": {
                        "$id": "#/properties/users/items/properties/username",
                        "type": "string",
                    },
                    "email": {
                        "$id": "#/properties/users/items/properties/email",
                        "type": "string",
                    }
                }
            }
        }
    }
}

def validate_users_json(json_object):
    try:
        validate(instance=json_object, schema=user_schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True