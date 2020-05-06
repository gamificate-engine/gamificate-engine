from app import app
from app.email import send_email
from flask import render_template


def send_api_key_email(admin, api_key, realm):
    send_email('[Gamificate] Your Realm API Key',
               sender=app.config['ADMINS'][0],
               recipients=[admin.email],
               text_body=render_template('email/api_key.txt', admin=admin, realm=realm, api_key=api_key),
               html_body=render_template('email/api_key.html', admin=admin, realm=realm, api_key=api_key))


def send_json_error_email(admin, realm):
    send_email('[Gamificate] Error uploading JSON file.',
               sender=app.config['ADMINS'][0],
               recipients=[admin.email],
               text_body=render_template('email/json_error.txt', admin=admin, realm=realm),
               html_body=render_template('email/json_error.html', admin=admin, realm=realm))