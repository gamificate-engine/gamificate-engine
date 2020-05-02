from app import app
from app.email import send_email
from flask import render_template


def send_api_key_email(admin, api_key, realm):
    send_email('[Gamificate] Your Realm API Key',
               sender=app.config['ADMINS'][0],
               recipients=[admin.email],
               text_body=render_template('email/api_key.txt', admin=admin, realm=realm, api_key=api_key),
               html_body=render_template('email/api_key.html', admin=admin, realm=realm, api_key=api_key))