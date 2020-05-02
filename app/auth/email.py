from app import app
from app.email import send_email
from flask import render_template


def send_password_reset_email(admin):
    token = admin.get_reset_password_token()
    send_email('[Gamificate] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[admin.email],
               text_body=render_template('email/reset_password.txt', admin=admin, token=token),
               html_body=render_template('email/reset_password.html', admin=admin, token=token))