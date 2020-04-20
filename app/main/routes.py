from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db, login
from app.main import bp

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('realms.realms'))

    return render_template('main/index.html')
