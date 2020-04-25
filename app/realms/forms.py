from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import ValidationError, DataRequired, InputRequired, Length, NumberRange, Email, EqualTo
from app.models import Admin
from flask_login import current_user



class RealmForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=32)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=1, max=256)])
    a = FloatField('a', validators=[InputRequired(), NumberRange(min=0, message="'a' cannot be less than 0.")])
    b = FloatField('b', validators=[InputRequired(), NumberRange(min=1, message="'b' cannot be less than 1.")])
    submit = SubmitField('Create Realm')

    def validate_name(self, name):
        admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()
        realms = admin.realms.all()

        for realm in realms:
            if realm.name == name.data:
                raise ValidationError('Please use a different name.')
    

class SettingsForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=32)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=32)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=128)])
    submit = SubmitField('Register')


    def validate_email(self, email):
        admin = Admin.query.filter_by(email=email.data).first()
        if admin is not None and admin.id_admin != current_user.get_id():
            raise ValidationError('Please use a different email address.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=24)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit2 = SubmitField('Request Password Reset')


class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])

    def validate_password(self, password):
        admin = Admin.query.filter_by(id_admin=current_user.get_id()).first_or_404()

        if not admin.checkPassword(password.data):
            raise ValidationError('Password inserted doesn\'t match.')
