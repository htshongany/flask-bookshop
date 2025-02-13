from app.extensions import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    # Relations
    book = db.relationship('Book', backref=db.backref('order_items', lazy=True))
    order = db.relationship('Order', backref=db.backref('order_items', lazy=True))

    def __repr__(self):
        return f'<OrderItem {self.id}>'
