from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Admin, Realm, Badge, User

class RealmForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Realm')

    def validate_name(self, name):
        realm = Realm.query.filter_by(name = name.data).first()
        if realm is not None:
            raise ValidationError('Please use a different name.')

    # Falta validação do premium


class BadgeForm(FlaskForm, realm):
    name = StringField('Name', validators=[DataRequired()])
    xp = IntegerField('XP', validators=[DataRequired()])
    required = IntegerField('XP required', validators=[DataRequired()])
    submit = SubmitField('Create Badge')

    badges = realm.badges.all()

    def validate_name(self, name):
       if [b.name for b in badges if b.name == name.data]:
            raise ValidationError('Please use a different name')

class UserForm(FlaskForm, realm):
    username = StringField('Username', validators=[DataRequired()])
    mail = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Create User')

    users = realm.users.all()

    def validate_username(self, username):
        if [u.username for u in users if u.username == username.data]:
           raise ValidationError('Username already in use. Try again.')

    def validate_mail(self,mail):
        if [u.email for u in users if u.email == email.data]:
            raise ValidationError('Email already in use. Try again.')