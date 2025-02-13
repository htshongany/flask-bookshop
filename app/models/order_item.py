# app/models/order_item.py

from app.extensions import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    # Attributs
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    # Relations
    order = db.relationship('Order', back_populates='order_items')
    book = db.relationship('Book', back_populates='order_items')

    # Méthodes
    def __repr__(self):
        return f'<OrderItem {self.id} - Order {self.order_id} - Book {self.book_id}>'
