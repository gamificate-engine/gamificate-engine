from app import app, db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm
from app.forms import LoginForm, RegistrationForm, RealmForm
from werkzeug.urls import url_parse
from flask import request


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('realms'))

    return render_template('webpage/index.html')



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

    return render_template('webpage/login.html', title='Sign In', form=form)


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
    return render_template('webpage/register.html', title='Register', form=form)


@app.route('/realms/') #/<admin_id>/')
@login_required
def realms():#admin_id):
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

    return render_template('realms/index.html', admin=admin, realms=admin.realms.all())#, admin=admin, realms=realms)



@app.route('/realms/new', methods=['GET', 'POST'])
@login_required
def new_realm():
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

    form = RealmForm()
    
    if form.validate_on_submit():
        realm = Realm(name = form.name.data, admin_id = current_user.get_id())

        db.session.add(realm)
        db.session.commit()

        flash('Congratulations, you created a new realm!')
        return redirect(url_for('realms'))
    
    return render_template('realms/new.html', admin=admin, form=form)


@app.route('/realms/<id>', methods=['GET', 'POST'])
@login_required
def show_realm(id):
    realm = Realm.query.filter_by(id_realm=id).first_or_404()
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

    
    return render_template('realms/show.html', realm=realm, admin=admin)


@app.route('/realms/<id>/badges')
@login_required
def badges(id):
    realm = Realm.query.filter_by(id_realm=id).first_or_404()
    admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

    return render_template('badges/index.html', realm=realm, admin=admin, badges=realm.badges.all())
