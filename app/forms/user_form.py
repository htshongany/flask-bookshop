from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class UserForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[
        Length(min=6),
        EqualTo('confirm_password', message='Les mots de passe doivent correspondre')
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[Length(min=6)])
    is_admin = BooleanField('Est administrateur')
    submit = SubmitField('Soumettre')
