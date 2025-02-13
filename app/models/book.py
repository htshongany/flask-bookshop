# app/models/book.py

from app.extensions import db
from sqlalchemy.orm import validates

class Book(db.Model):
    __tablename__ = 'books'

    # Attributs
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    available = db.Column(db.Boolean, default=True)

    # Relations
    ratings = db.relationship('Rating', back_populates='book', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', back_populates='book', lazy=True)

    # Méthodes
    def __repr__(self):
        return f'<Book {self.title}>'

    @property
    def average_rating(self):
        if self.ratings:
            total = sum(rating.score for rating in self.ratings)
            return total / len(self.ratings)
        else:
            return None

    def reduce_stock(self, quantity):
        if quantity > self.stock:
            raise ValueError('Stock insuffisant pour la quantité demandée.')
        self.stock -= quantity
        self.update_availability()

    def increase_stock(self, quantity):
        self.stock += quantity
        self.update_availability()

    def update_availability(self):
        self.available = self.stock > 0

    @validates('stock')
    def validate_stock(self, key, value):
        if value < 0:
            raise ValueError('Le stock ne peut pas être négatif.')
        return value
