from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class BookForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    author = StringField('Auteur', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = FloatField('Prix', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Enregistrer')
