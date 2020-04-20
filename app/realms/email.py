from flask_mail import Message
from app import app, mail
from flask import render_template


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_api_key_email(admin, api_key, realm):
    send_email('[Gamificate] Your Realm API Key',
               sender=app.config['ADMINS'][0],
               recipients=[admin.email],
               text_body=render_template('email/api_key.txt',
                                         admin=admin, realm=realm, api_key=api_key),
               html_body=render_template('email/api_key.html',
                                         admin=admin, realm=realm, api_key=api_key))