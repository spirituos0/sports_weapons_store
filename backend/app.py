from flask import Flask, render_template
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes import bp as api_bp
from cart_routes import cart_bp
from category_routes import category_bp
from flask_cors import CORS  # Добавляем импорт
from auth_routes import auth_bp
import sys
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)


db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)  # Инициализируем JWT
CORS(app)  # Разрешаем CORS для всего приложения

app.register_blueprint(api_bp, url_prefix='/api')  # Регистрируем Blueprint **только после создания app**
app.register_blueprint(cart_bp, url_prefix='/api')  # Регистрируем Blueprint корзины
app.register_blueprint(category_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route("/")  # <-- Добавляем маршрут
def home():
    return render_template("auth.html")  # Показываем HTML-страницу

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
