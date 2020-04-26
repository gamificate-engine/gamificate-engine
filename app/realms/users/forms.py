from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email

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