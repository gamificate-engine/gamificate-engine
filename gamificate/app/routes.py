from app import app, db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin
from app.forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse
from flask import request


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('realms'))

    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('realms'))

    form = LoginForm()
    
    if form.validate_on_submit(): #post
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin is None or not admin.checkPassword(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(admin, remember=form.remember_me.data)
        next_page = request.args.get('next')
        
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        admin = Admin(email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
        admin.setPassword(form.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/realms') #/<admin_id>/')
@login_required
def realms():#admin_id):
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()
    realms = [
        # {'name': 'Realm 1', 'body': 'Test #1'},
        # {'name': 'Realm 2', 'body': 'Test #1'}
    ]
    return render_template('realms.html', admin=admin, realms=realms, nr_realms=len(realms))#, admin=admin, realms=realms)
