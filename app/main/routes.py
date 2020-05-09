from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db, login, mail, app
from app.main import bp
from app.main.forms import ContactForm
from flask_mail import Message

@bp.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('realms.realms'))

    form = ContactForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            msg = Message(form.subject.data, sender=app.config['ADMINS'][0], recipients=[app.config['ADMINS'][0]])
            msg.body = """
            From: %s <%s>;

            %s
            """ % (form.name.data, form.email.data, form.message.data)
            mail.send(msg)
        
            return render_template('main/index.html', success=True, form=form)
        else:
            return render_template('main/index.html', success=False, form=form)

    elif request.method == 'GET':
        return render_template('main/index.html', form=form)


@bp.route('/api')
def api():
    return redirect('/api/')
