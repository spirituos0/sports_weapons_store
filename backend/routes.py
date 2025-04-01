from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from backend.models import User, Product, Order, OrderProduct, Cart, CartItem, Category
from backend import db  
from datetime import datetime


main_bp = Blueprint("main", __name__, url_prefix="/api")

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })

@main_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_list = [{'id': p.id, 'name': p.name, 'price': p.price, 'description': p.description, 'stock': p.stock} for p in products]
    return jsonify(products_list)

# Getting one product by ID
@main_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({'id': product.id, 'name': product.name, 'price': product.price, 'description': product.description, 'stock': product.stock})

# Creating new product
@main_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    category_id = data.get("category_id")
    if not data or not all(k in data for k in ('name', 'price', 'stock')):
        return jsonify({'error': 'Missing required fields'}), 400

    if category_id:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category is not found."}), 404

    new_product = Product(
        name=data["name"],
        price=data["price"],
        description=data.get("description"),
        stock=data["stock"],
        category_id=category_id,
    )

    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully', 'id': new_product.id}), 201

#Updating the product
@main_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'description' in data:
        product.description = data['description']
    if 'stock' in data:
        product.stock = data['stock']
    if 'category_id' in data:
        product.category_id = data['category_id']

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

# Deleting the product
@main_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})

# Getting all orders
@main_bp.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    orders_list = [
        {
            'id': order.id,
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'total_price': order.total_price,
            'status': order.status,
            'products': [
                {
                    'product_id': op.product_id,
                    'quantity': op.quantity
                } for op in order.products
            ]
        }
        for order in orders
    ]
    return jsonify(orders_list)

# Getting concrete order
@main_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({
        'id': order.id,
        'customer_name': order.customer_name,
        'customer_email': order.customer_email,
        'total_price': order.total_price,
        'status': order.status,
        'products': [
            {
                'product_id': op.product_id,
                'quantity': op.quantity
            } for op in order.products
        ]
    })

# Creating new order
@main_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data or not all(k in data for k in ('customer_name', 'customer_email', 'products')):
        return jsonify({'error': 'Missing required fields'}), 400

    total_price = 0
    new_order = Order(
        customer_name=data['customer_name'],
        customer_email=data['customer_email'],
        total_price=0  # Will count later
    )
    db.session.add(new_order)
    db.session.commit()

    for item in data['products']:
        product = Product.query.get(item['product_id'])
        if not product:
            return jsonify({'error': f'Product with ID {item["product_id"]} not found'}), 404
        if product.stock < item['quantity']:
            return jsonify({'error': f'Not enough stock for {product.name}'}), 400

        order_product = OrderProduct(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item['quantity']
        )
        db.session.add(order_product)

        product.stock -= item['quantity']  # We reduce the quantity of products
        total_price += product.price * item['quantity']

    new_order.total_price = total_price  # Update the price of the order
    db.session.commit()

    return jsonify({'message': 'Order created successfully', 'id': new_order.id}), 201

# Update the order status
@main_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()

    if 'status' in data:
        order.status = data['status']

    db.session.commit()
    return jsonify({'message': 'Order updated successfully'})

# Deleting the order
@main_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({"error": "Order not found or not yours"}), 404

    if order.status == "Shipped": # Only restore stock if order hasn't been shipped
        return jsonify({"error": "You can't delete shipped orders"}), 403

    user = User.query.get(user_id)

    # 1. Return product quantities back to stock
    
    for op in order.products:
        product = Product.query.get(op.product_id)
        if product:
            product.stock += op.quantity  # 👈 Return stock

    if user:
        user.balance += order.total_price

    # 2. Delete related OrderProduct records
    OrderProduct.query.filter_by(order_id=order_id).delete()

    # 3. Delete the order itself
    db.session.delete(order)
    db.session.commit()

    return jsonify({"message": "Order deleted and stock restored."}), 200

@main_bp.route("/purchase", methods=["POST"])
@jwt_required()
def purchase():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    products = data.get("products", [])

    if not products:
        return jsonify({"error": "No products specified"}), 400

    total_price = 0
    order_items = []

    for item in products:
        product = Product.query.get(item["product_id"])
        if not product:
            return jsonify({"error": f"Product ID {item['product_id']} not found"})
        if product.stock < item["quantity"]:
            return jsonify({"error": f"Not enough stock for {product.name}"}), 400

        # Calculate total price
        total_price += product.price * item["quantity"]
        order_items.append((product, item["quantity"]))

    # Check if user has enough balance

    if user.balance < total_price:
        return jsonify({"error": "Insufficient balance"}), 400

    # Deduct the balance and process order
    user.balance -= total_price
    db.session.commit()

    #Create order
    new_order = Order(
        user_id=user.id,
        customer_name=user.username,
        customer_email=user.email,
        total_price=total_price,
         created_at=datetime.utcnow()

    )
    db.session.add(new_order)
    db.session.commit()

    # Add order products
    for product, quantity in order_items:
        order_product = OrderProduct(
            order_id=new_order.id,
            product_id=product.id,
            quantity=quantity
        )
        db.session.add(order_product)
        product.stock -= quantity # Reduce stock
        db.session.commit()

    return jsonify({"message": "Purchase successful", "order_id": new_order.id, "remaining_balance": user.balance}), 201

@main_bp.route("/orders/user", methods=["GET"])
@jwt_required()
def get_user_orders():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    orders = Order.query.filter_by(user_id=user_id).order_by(Order.id.asc()).all()

    order_list = []
    for idx, order in enumerate(orders, start=1): # this adds per-user order number
        order_list.append({
            "id": order.id,
            "user_order_number": idx,
            "total_price": order.total_price,
            "status": order.status,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            "products": [
                {
                    "name": Product.query.get(op.product_id).name,
                    "quantity": op.quantity
                } for op in order.products
            ]
        })
    print("Order created_at:", order.created_at)
    return jsonify(order_list), 200   

