from flask import Blueprint

bp = Blueprint('realms', __name__)

from app.realms import routes
from app.realms.badges import routes
from app.realms.users import routes