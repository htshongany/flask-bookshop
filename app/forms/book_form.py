# app/forms/book_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileAllowed

class BookForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired(), Length(max=200)])
    author = StringField('Auteur', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    price = FloatField('Prix', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    available = BooleanField('Disponible')
    image = FileField('Image du livre', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images seulement!')])
