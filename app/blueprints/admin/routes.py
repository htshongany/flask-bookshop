from flask import render_template, redirect, url_for, flash, request
from . import admin_bp
from app.models.book import Book
from app.models.user import User
from app.models.order import Order
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

# Gestion des livres

@admin_bp.route('/books')
@admin_required
def manage_books():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)

    if query:
        books = Book.query.filter((Book.title.ilike(f'%{query}%')) | (Book.author.ilike(f'%{query}%'))).paginate(page=page, per_page=3)
    else:
        books = Book.query.paginate(page=page, per_page=3)
    
    return render_template('admin/book/manage_books.html', books=books, query=query)

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
    return render_template('admin/book/add_book.html', form=form)

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
    return render_template('admin/book/edit_book.html', form=form, book=book)

@admin_bp.route('/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Le livre a été supprimé avec succès.', 'success')
    return redirect(url_for('admin.manage_books'))

# Gestion des utilisateurs

@admin_bp.route('/users')
@admin_required
def manage_users():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)

    if query:
        users = User.query.filter((User.username.ilike(f'%{query}%')) | (User.email.ilike(f'%{query}%'))).paginate(page=page, per_page=3)
    else:
        users = User.query.paginate(page=page, per_page=3)
    
    return render_template('admin/user/manage_users.html', users=users, query=query)

@admin_bp.route('/users/view/<int:user_id>')
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user/view_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('L\'utilisateur a été supprimé avec succès.', 'success')
    return redirect(url_for('admin.manage_users'))

# Gestion des commandes

@admin_bp.route('/orders')
@admin_required
def manage_orders():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)

    if query:
        orders = Order.query.filter(Order.id.ilike(f'%{query}%')).paginate(page=page, per_page=3)
    else:
        orders = Order.query.paginate(page=page, per_page=3)
    
    return render_template('admin/order/manage_orders.html', orders=orders, query=query)

@admin_bp.route('/orders/view/<int:order_id>')
@admin_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order/view_order.html', order=order)

@admin_bp.route('/orders/delete/<int:order_id>', methods=['POST'])
@admin_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('La commande a été supprimée avec succès.', 'success')
    return redirect(url_for('admin.manage_orders'))
