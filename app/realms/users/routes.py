from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Realm, User
from app.realms import bp
from app.realms.users.forms import UserForm, JsonForm, EditForm
from app.realms.decorators import check_ownership, check_premium
import os
import json
from threading import Thread
from app.realms.email import send_json_error_email


@bp.route('/realms/<int:id>/users')
@login_required
@check_ownership
def users(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    page = request.args.get('page', 1, type=int)
    pagination = realm.users.paginate(page, app.config['USERS_PER_PAGE'], True)
    users = pagination.items
    next_url = url_for('realms.users', id=id, page=pagination.next_num) if pagination.has_next else None
    prev_url = url_for('realms.users', id=id, page=pagination.prev_num) if pagination.has_prev else None

    form_json = JsonForm()
    form_edit = EditForm()
    form_edit.realm = realm

    return render_template('realms/users/index.html', realm=realm, admin=admin, users=users,
                           form_json=form_json, form_edit=form_edit, next_url=next_url, prev_url=prev_url)


@bp.route('/realms/<int:id>/users/new', methods=['GET', 'POST'])
@login_required
@check_ownership
def new_user(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    form = UserForm()
    form.realm = realm

    if form.validate_on_submit():
        infoUser = {'username' : form.username.data, 'email': form.email.data}
        user = User()
        user.new_user(infoUser)

        realm.users.append(user)

        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you\'ve created a new user!')
        return redirect(url_for('realms.users', id = id))

    return render_template('realms/users/new.html', admin = admin, realm = realm, form = form)



def add_async_users_from_json(app, json, id_admin, id_realm, is_premium):
    with app.app_context():
        admin = Admin.query.get_or_404(id_admin)
        realm = Realm.query.get_or_404(id_realm)

        try:
            for user_info in json["users"]:
                user = User()
                user.new_user(user_info)

                if (User.query.filter_by(id_realm=id_realm, email=user.email).first() == None and 
                    User.query.filter_by(id_realm=id_realm, username=user.username).first() == None):
                    realm.users.append(user)
                else:
                    raise Exception("error")

            db.session.add(realm)
            db.session.commit()
            
        except Exception:
            db.session.rollback()
            send_json_error_email(admin, realm)

def add_users_from_json(json, id_admin, id_realm, is_premium):
    Thread(target=add_async_users_from_json, args=(app, json, id_admin, id_realm, is_premium)).start()



@bp.route('/realms/<int:id>/users/json', methods=['POST'])
@login_required
@check_ownership
@check_premium
def new_users_json(id):
    form = JsonForm(request.form)
    admin = Admin.query.get_or_404(current_user.get_id())

    if form.validate_on_submit():
        file = request.files['file']
        file.seek(0)
        json_obj = json.loads(file.read())

        add_users_from_json(json_obj, admin.id_admin, id, admin.premium)
        flash('Your file is being processed. You should see your new users at any moment! Any error will be sent to your email.')
    
    else:
        flash('Something went wrong. Check your file structure and try again.')

    return redirect(url_for('realms.users', id=id))


@bp.route('/realms/<int:id>/users/edit', methods=['POST'])
@login_required
@check_ownership
def edit_user(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    form = EditForm(request.form)
    form.realm = realm

    if form.validate_on_submit():
        user_id = form.id.data

        infoUser = {'username' : form.username.data, 'email': form.email.data}

        user = User.query.get_or_404(user_id)

        if user.id_realm != id:
            return render_template('errors/403.html'), 403
        else:
            user.from_dict(infoUser)
            db.session.commit()
            flash('User edited with success!')
    
    else:
        flash('Something went wrong. Please try again.')

    return redirect(url_for('realms.users', id=id))

@bp.route('/realms/<int:id>/users/delete', methods=['POST'])
@login_required
@check_ownership
def delete_user(id):
    realm = Realm.query.get_or_404(id)
    admin = Admin.query.get_or_404(current_user.get_id())

    user_id = request.args.get('user', None)
    if not user_id:
        return render_template('errors/404.html'), 404

    user = User.query.get_or_404(user_id)
    if user.id_realm != id:
        return render_template('errors/403.html'), 403
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted with success!')

    return redirect(url_for('realms.users', id=id))