from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField
from wtforms.validators import ValidationError, DataRequired, InputRequired
from app.models import Admin, Realm




class RealmForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    a = FloatField('a', validators=[InputRequired()])
    b = FloatField('b', validators=[InputRequired()])
    submit = SubmitField('Create Realm')

    def validate_name(self, name):
        realm = Realm.query.filter_by(name = name.data).first()
        if realm is not None:
            raise ValidationError('Please use a different name.')
    
    def validate_a(self, a):
        if float(a._value()) < 0:
            raise ValidationError('\'a\' cannot be less than 0.')

    def validate_b(self, b):
        if float(b._value()) < 1:
            raise ValidationError('\'b\' cannot be less than 1.')
