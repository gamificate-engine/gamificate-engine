from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from app.models import Badge


class BadgeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    xp = IntegerField('XP', validators=[DataRequired()])
    required = IntegerField('XP required', validators=[DataRequired()])
    submit = SubmitField('Create Badge')

    def validate_name(self, name):
        badge = Badge.query.filter_by(name = name.data).first()
        if badge is not None:
            raise ValidationError('Please use a different name')