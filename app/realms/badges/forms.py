from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Optional, Length

class BadgeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=32)])
    description = StringField('Description', validators=[DataRequired(), Length(min=3, max=256)])
    xp = IntegerField('XP', validators=[DataRequired()])
    required = IntegerField('XP required', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[Optional(), Length(min=3, max=2000)])
    id_reward = SelectField('Choose a Reward', coerce=int, validators=[Optional()])
    submit = SubmitField('Create Badge')

    def add_rewards(self):
        self.id_reward.choices = [(0, 'Choose a Reward')] + [(r.id_reward, r.name) for r in self.realm.rewards.all()]

    def validate_name(self, name):
        badges = self.realm.badges.all()

        if [b.name for b in badges if b.name == name.data]:
            raise ValidationError('Please use a different name')

class EditForm(FlaskForm):
    id = IntegerField("ID", validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=32)])
    description = StringField('Description', validators=[DataRequired(), Length(min=3, max=256)])
    image_url = StringField('Image URL', validators=[Optional(), Length(min=3, max=2000)])
    submit = SubmitField('Edit Badge')

    def validate_name(self, name):
        badges = self.realm.badges.all()

        if [b.name for b in badges if b.name == name.data and self.id.data != b.id_badge]:
            raise ValidationError('Please use a different name')