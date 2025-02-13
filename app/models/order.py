# app/models/order.py

from app.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    # Attributs
    id = db.Column(db.Integer, primary_key=True)
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='En attente')

    # Relations
    user = db.relationship('User', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order', lazy=True, cascade='all, delete-orphan')

    # Méthodes
    def __repr__(self):
        return f'<Order {self.id}>'
