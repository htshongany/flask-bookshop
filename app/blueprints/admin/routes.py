from flask import render_template, redirect, url_for, flash, request
from . import admin_bp
from app.models.book import Book
from app.forms.book_form import BookForm
from app.extensions import db
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.exceptions import abort

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Accès interdit
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/books')
@admin_required
def manage_books():
    books = Book.query.all()
    return render_template('admin/manage_books.html', books=books)

@admin_bp.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data
        )
        db.session.add(book)
        db.session.commit()
        flash('Le livre a été ajouté avec succès.', 'success')
        return redirect(url_for('admin.manage_books'))
    return render_template('admin/add_book.html', form=form)

@admin_bp.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.description = form.description.data
        book.price = form.price.data
        book.stock = form.stock.data
        db.session.commit()
        flash('Le livre a été mis à jour avec succès.', 'success')
        return redirect(url_for('admin.manage_books'))
    return render_template('admin/edit_book.html', form=form, book=book)

@admin_bp.route('/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Le livre a été supprimé avec succès.', 'success')
    return redirect(url_for('admin.manage_books'))
