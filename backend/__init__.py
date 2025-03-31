from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from backend.config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, template_folder="C:/Users/tilto/Shop Site/templates", static_folder="C:/Users/tilto/Shop Site/static")
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from backend import models  

    with app.app_context():
        db.create_all()  # Will create tables if they don't exist

    from backend.auth_routes import auth_bp
    from backend.routes import main_bp
    from backend.cart_routes import cart_bp
    from backend.category_routes import category_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(cart_bp, url_prefix="")
    app.register_blueprint(category_bp, url_prefix="/categories")

    return app
