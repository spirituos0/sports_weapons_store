from backend import create_app, db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from backend.config import Config
from flask_cors import CORS  # Разрешает CORS
from flask import Flask, render_template



app = create_app()
app.config.from_object(Config)
migrate = Migrate(app, db)



jwt = JWTManager(app)  # Инициализируем JWT
CORS(app, supports_credentials=True)  # Разрешаем куки в CORS

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/")  # <-- Добавляем маршрут
def home():
    return render_template("auth.html")  # Показываем HTML-страницу

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/products")
def products():
    return render_template("products.html")  # Flask загрузит файл из templates/

if __name__ == "__main__":
    app.run(debug=True)
