import os
from functools import wraps
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.exceptions import HTTPException, abort
from werkzeug.utils import secure_filename
from . import admin_bp
from app.models.book import Book
from app.models.user import User
from app.models.order import Order
from app.models.order_item import OrderItem
from app.forms.book_form import BookForm
from app.forms.user_form import UserForm
from app.forms.order_form import OrderForm
from app.extensions import db

# Extensions autorisées pour l'upload d'images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Décorateur : accès réservé à l'admin ou au staff
def admin_or_staff_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['admin', 'staff']:
            abort(403)  # Interdit si pas admin ou staff
        return f(*args, **kwargs)
    return decorated_function

# Restriction globale : toutes les routes du blueprint demandent admin/staff
@admin_bp.before_request
def restrict_to_admins_and_staff():
    if not current_user.is_authenticated or current_user.role not in ['admin', 'staff']:
        abort(403)

@admin_bp.route('/dashboard')
@admin_or_staff_required
def dashboard():
    return render_template('admin/dashboard.html')

# -------------------------------
# GESTION DES LIVRES
# -------------------------------
@admin_bp.route('/books')
@admin_or_staff_required
def manage_books():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)

    if query:
        books = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) | (Book.author.ilike(f'%{query}%'))
        ).paginate(page=page, per_page=3)
    else:
        books = Book.query.paginate(page=page, per_page=3)
    
    return render_template('admin/book/manage_books.html', books=books, query=query)

@admin_bp.route('/books/add', methods=['GET', 'POST'])
@admin_or_staff_required
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
        # Gestion de l'upload de l'image
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            if not allowed_file(filename):
                flash("Format de fichier non autorisé. Seules les images (png, jpg, jpeg, gif) sont autorisées.", 'danger')
                return redirect(url_for('admin.add_book'))
            try:
                upload_path = os.path.join(current_app.root_path, 'static', 'images', 'books')
                os.makedirs(upload_path, exist_ok=True)
                form.image.data.save(os.path.join(upload_path, filename))
                book.image = filename
            except Exception as e:
                flash("Erreur lors de l'upload de l'image.", 'danger')
                return redirect(url_for('admin.add_book'))
        else:
            book.image = 'default_book.jpeg'
        try:
            db.session.add(book)
            db.session.commit()
            flash('Le livre a été ajouté avec succès.', 'success')
            return redirect(url_for('admin.manage_books'))
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue lors de l'ajout du livre.", 'danger')
    return render_template('admin/book/add_book.html', form=form)

@admin_bp.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_or_staff_required
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

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            if not allowed_file(filename):
                flash("Format de fichier non autorisé. Seules les images (png, jpg, jpeg, gif) sont autorisées.", 'danger')
                return redirect(url_for('admin.edit_book', book_id=book_id))
            try:
                upload_path = os.path.join(current_app.root_path, 'static', 'images', 'books')
                os.makedirs(upload_path, exist_ok=True)
                form.image.data.save(os.path.join(upload_path, filename))
                book.image = filename
            except Exception as e:
                flash("Erreur lors de l'upload de l'image.", 'danger')
                return redirect(url_for('admin.edit_book', book_id=book_id))
        try:
            db.session.commit()
            flash('Le livre a été mis à jour avec succès.', 'success')
            return redirect(url_for('admin.manage_books'))
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue lors de la mise à jour du livre.", 'danger')
    return render_template('admin/book/edit_book.html', form=form, book=book)

@admin_bp.route('/books/delete/<int:book_id>', methods=['POST'])
@admin_or_staff_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    try:
        db.session.delete(book)
        db.session.commit()
        flash('Le livre a été supprimé avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash("Une erreur est survenue lors de la suppression du livre.", 'danger')
    return redirect(url_for('admin.manage_books'))

# -------------------------------
# GESTION DES UTILISATEURS
# -------------------------------
@admin_bp.route('/users')
@admin_or_staff_required
def manage_users():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)

    if query:
        users = User.query.filter(
            (User.username.ilike(f'%{query}%')) | (User.email.ilike(f'%{query}%'))
        ).paginate(page=page, per_page=3)
    else:
        users = User.query.paginate(page=page, per_page=3)
    
    return render_template('admin/user/manage_users.html', users=users, query=query)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_or_staff_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        # Si l'utilisateur courant est admin, on prend le rôle sélectionné.
        # Sinon, on force le rôle à 'staff' ou 'customer' seulement.
        if current_user.role == 'admin':
            role = form.role.data  # admin, staff ou customer
        else:
            # Le staff n'a pas le droit de créer un admin,
            # donc si le form renvoie 'admin', on le force à 'staff'.
            if form.role.data == 'admin':
                role = 'staff'
            else:
                role = form.role.data

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role=role
        )
        new_user.set_password(form.password.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("L'utilisateur a été ajouté avec succès.", 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue lors de l'ajout de l'utilisateur.", 'danger')
    return render_template('admin/user/add_user.html', form=form)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_or_staff_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data

        if current_user.role == 'admin':
            user.role = form.role.data
        else:
            if form.role.data == 'admin':
                user.role = 'staff'
            else:
                user.role = form.role.data

        if form.password.data:
            user.set_password(form.password.data)

        try:
            db.session.commit()
            flash("L'utilisateur a été mis à jour avec succès.", 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue lors de la mise à jour de l'utilisateur.", 'danger')
    return render_template('admin/user/edit_user.html', form=form, user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_or_staff_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash("L'utilisateur a été supprimé avec succès.", 'success')
    except Exception as e:
        db.session.rollback()
        flash("Une erreur est survenue lors de la suppression de l'utilisateur.", 'danger')
    return redirect(url_for('admin.manage_users'))

# -------------------------------
# GESTION DES COMMANDES
# -------------------------------
@admin_bp.route('/orders')
@admin_or_staff_required
def manage_orders():
    query = request.args.get('query', '')
    validated = request.args.get('validated')
    not_validated = request.args.get('not_validated')
    page = request.args.get('page', 1, type=int)

    filters = []
    if validated:
        filters.append(Order.status == 'Validée')
    if not_validated:
        filters.append(Order.status != 'Validée')

    orders_query = Order.query.filter(*filters)
    if query:
        search = f'%{query}%'
        orders_query = orders_query.join(User, User.id == Order.user_id)\
            .outerjoin(OrderItem, OrderItem.order_id == Order.id)\
            .outerjoin(Book, Book.id == OrderItem.book_id)\
            .filter(
                (User.username.ilike(search)) |
                (Book.title.ilike(search)) |
                (Book.author.ilike(search))
            ).distinct()

    orders = orders_query.order_by(Order.status.asc()).paginate(page=page, per_page=3)

    total_validated_price = db.session.query(
        db.func.sum(Book.price * OrderItem.quantity)
    ).select_from(OrderItem).join(Order).filter(Order.status == 'Validée').scalar() or 0

    total_not_validated_price = db.session.query(
        db.func.sum(Book.price * OrderItem.quantity)
    ).select_from(OrderItem).join(Order).filter(Order.status != 'Validée').scalar() or 0

    return render_template(
        'admin/order/manage_orders.html',
        orders=orders,
        query=query,
        total_validated_price=total_validated_price,
        total_not_validated_price=total_not_validated_price
    )

@admin_bp.route('/orders/add', methods=['GET', 'POST'])
@admin_or_staff_required
def add_order():
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(
            user_id=form.user_id.data,
            status=form.status.data
        )
        try:
            db.session.add(order)
            db.session.commit()
            flash('La commande a été ajoutée avec succès.', 'success')
            return redirect(url_for('admin.manage_orders'))
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue lors de l'ajout de la commande.", 'danger')
    return render_template('admin/order/add_order.html', form=form)

@admin_bp.route('/orders/edit/<int:order_id>', methods=['GET', 'POST'])
@admin_or_staff_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderForm(obj=order)
    if form.validate_on_submit():
        order.user_id = form.user_id.data
        order.status = form.status.data
        try:
            db.session.commit()
            flash('La commande a été mise à jour avec succès.', 'success')
            return redirect(url_for('admin.manage_orders'))
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue lors de la mise à jour de la commande.", 'danger')
    return render_template('admin/order/edit_order.html', form=form, order=order)

@admin_bp.route('/orders/validate/<int:order_id>', methods=['POST'])
@admin_or_staff_required
def validate_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Validée'
    try:
        db.session.commit()
        flash('La commande a été validée avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash("Une erreur est survenue lors de la validation de la commande.", 'danger')
    return redirect(url_for('admin.manage_orders'))

@admin_bp.route('/orders/delete/<int:order_id>', methods=['POST'])
@admin_or_staff_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'Validée':
        try:
            for item in order.order_items:
                item.book.increase_stock(item.quantity)
            db.session.delete(order)
            db.session.commit()
            flash('La commande a été annulée et les livres ont été retournés au stock.', 'success')
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue lors de l'annulation de la commande.", 'danger')
    else:
        flash("L'annulation n'est pas possible car la commande a déjà été validée.", 'danger')
    return redirect(url_for('admin.manage_orders'))

@admin_bp.route('/orders/details/<int:order_id>')
@admin_or_staff_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order/order_details.html', order=order)

# -------------------------------
# GESTION DES ERREURS
# -------------------------------
@admin_bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@admin_bp.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

# Optionnel : gestion globale de l'erreur 500
# @admin_bp.errorhandler(Exception)
# def handle_exception(e):
#     if isinstance(e, HTTPException):
#         return e
#     return render_template('errors/500.html'), 500
