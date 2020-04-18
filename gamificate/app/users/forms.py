from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from app.models import User


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    mail = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
           raise ValidationError('Username already in use. Try again.')

    def validate_mail(self,mail):
        user = User.query.filter_by(email=mail.data).first()
        if user is not None:
            raise ValidationError('Email already in use. Try again.')
