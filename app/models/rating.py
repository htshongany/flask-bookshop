# app/models/rating.py

from app.extensions import db

class Rating(db.Model):
    __tablename__ = 'ratings'

    # Attributs
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    # Contrainte d'unicité pour empêcher un utilisateur de noter plusieurs fois le même livre
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='user_book_unique'),)

    # Relations
    user = db.relationship('User', back_populates='ratings')
    book = db.relationship('Book', back_populates='ratings')

    # Méthodes
    def __repr__(self):
        return f'<Rating {self.score} by User {self.user_id} for Book {self.book_id}>'
