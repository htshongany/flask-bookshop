from app.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relations
    # Si 'order_items' est déjà défini via le backref dans 'OrderItem', il n'est pas nécessaire de le redéfinir ici.

    def __repr__(self):
        return f'<Order {self.id}>'

