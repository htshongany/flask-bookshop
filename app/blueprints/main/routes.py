from flask import render_template, request, redirect, url_for, session, flash
from . import main_bp
from app.models.book import Book
from app.models.order import Order
from app.models.order_item import OrderItem
from app.extensions import db
from flask_login import login_required, current_user

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/catalogue')
def catalogue():
    books = Book.query.all()
    return render_template('main/catalogue.html', books=books)

@main_bp.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('main/book_details.html', book=book)

# Route pour ajouter un livre au panier
@main_bp.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    cart = session.get('cart', {})
    quantity_in_cart = cart.get(str(book_id), 0)
    
    if book.stock > quantity_in_cart:
        cart[str(book_id)] = quantity_in_cart + 1
        session['cart'] = cart
        flash(f'Le livre "{book.title}" a été ajouté à votre panier.', 'success')
    else:
        flash(f'Le stock est insuffisant pour ajouter ce livre.', 'warning')
    return redirect(url_for('main.catalogue'))

# Route pour afficher le panier
@main_bp.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for book_id, quantity in cart.items():
        book = Book.query.get(int(book_id))
        if book:
            subtotal = book.price * quantity
            total += subtotal
            items.append({
                'book': book,
                'quantity': quantity,
                'subtotal': subtotal
            })
    return render_template('main/cart.html', books=items, total=total)

# Route pour mettre à jour la quantité d'un article dans le panier
@main_bp.route('/update_cart/<int:book_id>', methods=['POST'])
def update_cart(book_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    book = Book.query.get_or_404(book_id)
    if str(book_id) in cart:
        if quantity > 0:
            if quantity <= book.stock:
                cart[str(book_id)] = quantity
                session['cart'] = cart
                flash('Le panier a été mis à jour.', 'success')
            else:
                flash(f'Le stock est insuffisant pour la quantité demandée du livre "{book.title}".', 'warning')
        else:
            del cart[str(book_id)]
            session['cart'] = cart
            flash('Le livre a été retiré du panier.', 'info')
    else:
        flash('Le livre n\'est pas dans le panier.', 'warning')
    return redirect(url_for('main.cart'))

# Route pour vider le panier
@main_bp.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    flash('Votre panier a été vidé.', 'info')
    return redirect(url_for('main.cart'))

# Route pour passer la commande
@main_bp.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('main.cart'))
    order = Order(user_id=current_user.id)
    db.session.add(order)
    db.session.commit()  # Nécessaire pour obtenir l'ID de la commande
    for book_id, quantity in cart.items():
        book = Book.query.get(int(book_id))
        if book:
            if book.stock >= quantity:
                order_item = OrderItem(
                    quantity=quantity,
                    order_id=order.id,
                    book_id=book.id
                )
                db.session.add(order_item)
                book.stock -= quantity  # Mise à jour du stock
            else:
                flash(f'Stock insuffisant pour le livre "{book.title}".', 'warning')
                db.session.rollback()
                return redirect(url_for('main.cart'))
        else:
            flash(f'Le livre avec l\'ID {book_id} n\'existe pas.', 'warning')
            db.session.rollback()
            return redirect(url_for('main.cart'))
    db.session.commit()
    session.pop('cart', None)
    flash('Votre commande a été passée avec succès !', 'success')
    return redirect(url_for('main.index'))

# Route pour voir les commandes de l'utilisateur
@main_bp.route('/my_orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_ordered.desc()).all()
    return render_template('main/my_orders.html', orders=orders)
