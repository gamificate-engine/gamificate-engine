from app import db
from app.auth import bp
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from app.models import Admin
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from werkzeug.urls import url_parse
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('realms.realms'))

    form = LoginForm()
    
    if form.validate_on_submit(): #post
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin is None or not admin.checkPassword(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(admin, remember=form.remember_me.data)
        next_page = request.args.get('next')
        
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))



@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        admin = Admin(email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
        admin.setPassword(form.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin:
            send_password_reset_email(admin)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    admin = Admin.verify_reset_password_token(token)
    if not admin:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        admin.setPassword(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)