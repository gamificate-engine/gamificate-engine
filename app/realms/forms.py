from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Admin, Realm




class RealmForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Realm')

    def validate_name(self, name):
        realm = Realm.query.filter_by(name = name.data).first()
        if realm is not None:
            raise ValidationError('Please use a different name.')

    # Falta validação do premium