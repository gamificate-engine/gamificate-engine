from flask import Blueprint

bp = Blueprint('realms', __name__)

from app.realms import routes
