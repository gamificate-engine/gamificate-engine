from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api.routes import users, leaderboards, auth, badges, rewards
from app.api import errors