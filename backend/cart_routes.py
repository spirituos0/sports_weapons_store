from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models import Cart, CartItem, Product

cart_bp = Blueprint('cart', __name__)

# Get cart contents
@cart_bp.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart or not cart.items:
        return jsonify({"message": "The cart is empty"}), 200

    cart_items = [
        {
            "product_id": item.product_id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": item.product.price
        }
        for item in cart.items
    ]
    return jsonify(cart_items), 200

# Add product to cart
@cart_bp.route('/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Checking if the user already has a cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    # Checking if the item is already in the cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

    # Calculate the total number of items in the basket
    total_quantity = quantity if not cart_item else cart_item.quantity + quantity

    # We check if there is enough product in stock
    if total_quantity > product.stock:
        return jsonify({"error": f"Only {product.stock} items available in stock"}), 400

    # Add or update a product in the cart
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "Product added to cart"}), 201

# Remove item from cart
@cart_bp.route('/cart/remove', methods=['POST'])
@jwt_required()
def remove_from_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get("product_id")

    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({"error": "Product not found in cart"}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Product removed from cart"}), 200

# Clear Cart 
@cart_bp.route('/cart/clear', methods=['POST'])
@jwt_required()
def clear_cart():
    user_id = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return jsonify({"message": "Cart is already empty"}), 200

    for item in cart.items:
        db.session.delete(item)

    db.session.commit()
    return jsonify({"message": "Cart cleared"}), 200
