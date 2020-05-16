from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, IntegerField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email, Optional
from flask import request
from werkzeug.utils import secure_filename
from app.realms.validation import validate_users_json
import json


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Create User')


    def validate_username(self, username):
        users = self.realm.users.all()

        if [u.username for u in users if u.username == username.data]:
           raise ValidationError('Username already in use. Try again.')

    def validate_email(self, email):
        users = self.realm.users.all()

        if [u.email for u in users if u.email == email.data]:
            raise ValidationError('Email already in use. Try again.')



class JsonForm(FlaskForm):
    file = FileField('file')

    def validate_file(self, file):
        file = request.files['file']

        if not '.json' in file.filename:
            raise ValidationError('File extension not supported.')

        filename = secure_filename(file.filename)
        json_obj = json.loads(file.read())

        if not validate_users_json(json_obj):
            raise ValidationError('Wrong file structure.')

class EditForm(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    active = BooleanField('Active', validators=[Optional()])
    submit = SubmitField('Edit User')


    def validate_username(self, username):
        users = self.realm.users.all()

        if [u.username for u in users if u.username == username.data and u.id_user != self.id.data]:
           raise ValidationError('Username already in use. Try again.')

    def validate_email(self, email):
        users = self.realm.users.all()

        if [u.email for u in users if u.email == email.data and u.id_user != self.id.data]:
            raise ValidationError('Email already in use. Try again.')
