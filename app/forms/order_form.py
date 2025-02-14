from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from app.models.user import User

class OrderForm(FlaskForm):
    user_id = SelectField('Utilisateur', coerce=int, validators=[DataRequired()])
    status = SelectField('Statut', choices=[
        ('En attente', 'En attente'),
        ('En cours', 'En cours'),
        ('Livrée', 'Livrée'),
        ('Annulée', 'Annulée')
    ], validators=[DataRequired()])
    submit = SubmitField('Soumettre')

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.user_id.choices = [(user.id, user.username) for user in User.query.order_by(User.username).all()]
