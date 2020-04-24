from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField
from wtforms.validators import ValidationError, DataRequired, InputRequired, Length, NumberRange
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
    
