from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import ValidationError, DataRequired

class BadgeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    xp = IntegerField('XP', validators=[DataRequired()])
    required = IntegerField('XP required', validators=[DataRequired()])
    submit = SubmitField('Create Badge')

    

    def validate_name(self, name):
        badges = self.realm.badges.all()

        if [b.name for b in badges if b.name == name.data]:
            raise ValidationError('Please use a different name')