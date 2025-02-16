from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_login import current_user

class UserForm(FlaskForm):
    username = StringField(
        "Nom d'utilisateur",
        validators=[DataRequired(), Length(min=2, max=150)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        "Mot de passe",
        validators=[
            Length(min=6),
            EqualTo('confirm_password', message='Les mots de passe doivent correspondre')
        ]
    )
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[Length(min=6)]
    )
    role = SelectField(
        "Rôle",
        choices=[],  # Choices seront définis dynamiquement
        validators=[DataRequired()]
    )
    submit = SubmitField("Soumettre")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adaptation dynamique des choix en fonction du rôle
        if current_user.is_authenticated and current_user.role == 'admin':
            self.role.choices = [
                ('customer', 'Customer'),
                ('staff', 'Staff'),
                ('admin', 'Admin')
            ]
        else:
            self.role.choices = [
                ('customer', 'Customer'),
                ('staff', 'Staff')
            ]