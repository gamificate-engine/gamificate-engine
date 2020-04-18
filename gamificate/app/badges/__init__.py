from flask import Blueprint

bp = Blueprint('badges', __name__)

from app.badges import routes