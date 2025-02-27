from flask import Blueprint, request, jsonify
from backend.models import db, Category

category_bp = Blueprint("category", __name__)

# Получить все категории
@category_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify([{"id": c.id, "name": c.name} for c in categories])

# Добавить новую категорию
@category_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    new_category = Category(name=data["name"])
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message": "Category created successfully!"}), 201

# Удалить категорию
@category_bp.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted successfully!"})
