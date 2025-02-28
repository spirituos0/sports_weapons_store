from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from models import User, Product, Order, OrderProduct, db, Cart, CartItem, Category


bp = Blueprint("api", __name__)  # Создаем Blueprint

@bp.route("/profile", methods=["GET"])
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

@bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_list = [{'id': p.id, 'name': p.name, 'price': p.price, 'description': p.description, 'stock': p.stock} for p in products]
    return jsonify(products_list)

# Получение одного продукта по ID
@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({'id': product.id, 'name': product.name, 'price': product.price, 'description': product.description, 'stock': product.stock})

# Создание нового продукта
@bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    category_id = data.get("category_id")
    if not data or not all(k in data for k in ('name', 'price', 'description', 'stock')):
        return jsonify({'error': 'Missing required fields'}), 400

    if category_id:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Категория не найдена"}), 404

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

# Обновление продукта
@bp.route('/products/<int:product_id>', methods=['PUT'])
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
        category = data['category_id']

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

# Удаление продукта
@bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})

# Получение всех заказов
@bp.route('/orders', methods=['GET'])
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

# Получение конкретного заказа
@bp.route('/orders/<int:order_id>', methods=['GET'])
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

# Создание нового заказа
@bp.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data or not all(k in data for k in ('customer_name', 'customer_email', 'products')):
        return jsonify({'error': 'Missing required fields'}), 400

    total_price = 0
    new_order = Order(
        customer_name=data['customer_name'],
        customer_email=data['customer_email'],
        total_price=0  # Посчитаем позже
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

        product.stock -= item['quantity']  # Уменьшаем количество товара
        total_price += product.price * item['quantity']

    new_order.total_price = total_price  # Обновляем цену заказа
    db.session.commit()

    return jsonify({'message': 'Order created successfully', 'id': new_order.id}), 201

# Обновление статуса заказа
@bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()

    if 'status' in data:
        order.status = data['status']

    db.session.commit()
    return jsonify({'message': 'Order updated successfully'})

# Удаление заказа
@bp.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({"message": "Order not found"}), 404

    # Удаляем связанные товары
    OrderProduct.query.filter_by(order_id=order_id).delete()

    # Теперь можно удалить сам заказ
    db.session.delete(order)
    db.session.commit()

    return jsonify({"message": "Order deleted successfully"}), 200

