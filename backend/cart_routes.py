from flask import Blueprint, request, jsonify
from backend.models import db, Cart, CartItem, Product
from flask_jwt_extended import jwt_required, get_jwt_identity


cart_bp = Blueprint('cart', __name__)


# Получить содержимое корзины
@cart_bp.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return jsonify({"message": "The cart is empty"}), 200

    cart_items = [
        {
            "product_id": item.product_id,
            "quantity": item.quantity
        }
        for item in cart.items
    ]
    return jsonify(cart_items), 200

# Добавить товар в корзину
@cart_bp.route('/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "The product is not found"}), 404

    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "The product is added to the cart"}), 201

# Удалить товар из корзины
@cart_bp.route('/cart/remove', methods=['POST'])
@jwt_required()
def remove_from_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get("product_id")

    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return jsonify({"message": "The cart is empty"}), 404

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({"message": "The product is not found in the cart"}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "The product is deleted from the cart"}), 200

# Очистить корзину
@cart_bp.route('/cart/clear', methods=['POST'])
@jwt_required()
def clear_cart():
    user_id = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return jsonify({"message": "The cart is empty"}), 404

    for item in cart.items:
        db.session.delete(item)

    db.session.commit()
    return jsonify({"message": "The cart is empty"}), 200