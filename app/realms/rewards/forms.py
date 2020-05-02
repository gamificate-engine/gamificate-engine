from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Optional, Length

class RewardForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=32)])
    desc = StringField('Description', validators=[DataRequired(), Length(min=3, max=256)])
    submit = SubmitField('Create Reward')

    def validate_name(self, name):
        rewards = self.realm.rewards.all()

        if [r.name for r in rewards if r.name == name.data]:
            raise ValidationError('Please use a different name')