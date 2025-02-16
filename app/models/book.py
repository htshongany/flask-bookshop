# app/models/book.py
from app.extensions import db
from sqlalchemy.orm import validates
from datetime import datetime
from PIL import Image
import os

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
    image = db.Column(db.String(120), nullable=True)  # Nouveau champ pour l'image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Date de création
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Date de mise à jour

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

    def save_image(self, image_file):
        filename = f'book_{self.id}.jpg'
        filepath = os.path.join('app', 'static', 'images', 'books', filename)

        # Redimensionner l'image
        image = Image.open(image_file)
        image.thumbnail((300, 300))
        image.save(filepath)

        self.image = filename
        db.session.commit()
