from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email

class UserForm(FlaskForm, realm):
    username = StringField('Username', validators=[DataRequired()])
    mail = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Create User')

    users = realm.users.all()

    def validate_username(self, username):
        if [u.username for u in users if u.username == username.data]:
           raise ValidationError('Username already in use. Try again.')

    def validate_mail(self,mail):
        if [u.email for u in users if u.email == email.data]:
            raise ValidationError('Email already in use. Try again.')