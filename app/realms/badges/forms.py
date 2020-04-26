from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import ValidationError, DataRequired

class BadgeForm(FlaskForm, realm):
    name = StringField('Name', validators=[DataRequired()])
    xp = IntegerField('XP', validators=[DataRequired()])
    required = IntegerField('XP required', validators=[DataRequired()])
    submit = SubmitField('Create Badge')

    badges = realm.badges.all()

    def validate_name(self, name):
       if [b.name for b in badges if b.name == name.data]:
            raise ValidationError('Please use a different name')