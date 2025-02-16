# app/bleauprints/admin/routes.py
from flask import render_template, redirect, url_for, flash, request
from . import admin_bp
from app.models.book import Book
from app.models.user import User
from app.models.order import Order
from app.models.order_item import OrderItem
from app.forms.book_form import BookForm
from app.forms.user_form import UserForm
from app.forms.order_form import OrderForm
from app.extensions import db
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import os

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
            stock=form.stock.data,
            available=form.available.data
        )
        db.session.add(book)
        db.session.commit()

        # Gestion de l'upload de l'image
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join('app', 'static', 'images', 'books', filename))
            book.image = filename
        else:
            # Si aucune image n'est téléchargée, utilisez une image par défaut
            book.image = 'default_book.jpeg'
        
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
        book.available = form.available.data

        # Gestion de l'upload de l'image
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join('app', 'static', 'images', 'books', filename))
            book.image = filename

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

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('L\'utilisateur a été ajouté avec succès.', 'success')
        return redirect(url_for('admin.manage_users'))
    return render_template('admin/user/add_user.html', form=form)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('L\'utilisateur a été mis à jour avec succès.', 'success')
        return redirect(url_for('admin.manage_users'))
    return render_template('admin/user/edit_user.html', form=form, user=user)

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
    validated = request.args.get('validated')
    not_validated = request.args.get('not_validated')
    page = request.args.get('page', 1, type=int)

    # Construction des filtres de statut
    filters = []
    if validated:
        filters.append(Order.status == 'Validée')
    if not_validated:
        filters.append(Order.status != 'Validée')

    # Construction de la requête de base
    orders_query = Order.query.filter(*filters)

    # Application des filtres de recherche si une requête existe
    if query:
        query = f'%{query}%'
        orders_query = orders_query \
            .join(User, User.id == Order.user_id) \
            .outerjoin(OrderItem, OrderItem.order_id == Order.id) \
            .outerjoin(Book, Book.id == OrderItem.book_id) \
            .filter(
                (User.username.ilike(query)) |
                (Book.title.ilike(query)) |
                (Book.author.ilike(query))
            ) \
            .distinct()

    # Pagination et tri
    orders = orders_query.order_by(Order.status.asc()).paginate(page=page, per_page=3)

    # Calcul des totaux
    total_validated_price = db.session.query(db.func.sum(Book.price * OrderItem.quantity)).select_from(OrderItem).join(Order).filter(Order.status == 'Validée').scalar() or 0
    total_not_validated_price = db.session.query(db.func.sum(Book.price * OrderItem.quantity)).select_from(OrderItem).join(Order).filter(Order.status != 'Validée').scalar() or 0

    return render_template(
        'admin/order/manage_orders.html',
        orders=orders,
        query=query,
        total_validated_price=total_validated_price,
        total_not_validated_price=total_not_validated_price
    )


@admin_bp.route('/orders/add', methods=['GET', 'POST'])
@admin_required
def add_order():
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(
            user_id=form.user_id.data,
            status=form.status.data
        )
        db.session.add(order)
        db.session.commit()
        flash('La commande a été ajoutée avec succès.', 'success')
        return redirect(url_for('admin.manage_orders'))
    return render_template('admin/order/add_order.html', form=form)

@admin_bp.route('/orders/edit/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderForm(obj=order)
    if form.validate_on_submit():
        order.user_id = form.user_id.data
        order.status = form.status.data
        db.session.commit()
        flash('La commande a été mise à jour avec succès.', 'success')
        return redirect(url_for('admin.manage_orders'))
    return render_template('admin/order/edit_order.html', form=form, order=order)

@admin_bp.route('/orders/validate/<int:order_id>', methods=['POST'])
@admin_required
def validate_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Validée'
    db.session.commit()
    flash('La commande a été validée avec succès.', 'success')
    return redirect(url_for('admin.manage_orders'))

@admin_bp.route('/orders/delete/<int:order_id>', methods=['POST'])
@admin_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'Validée':
        for item in order.order_items:
            item.book.increase_stock(item.quantity)
        db.session.delete(order)
        db.session.commit()
        flash('La commande a été annulée et les livres ont été retournés au stock.', 'success')
    else:
        flash('L\'annulation n\'est pas possible car la commande a déjà été validée.', 'danger')
    return redirect(url_for('admin.manage_orders'))

@admin_bp.route('/orders/details/<int:order_id>')
@admin_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order/order_details.html', order=order)
