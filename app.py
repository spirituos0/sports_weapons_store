from backend import create_app, db
from flask_jwt_extended import JWTManager
from backend.config import Config
from flask_cors import CORS  # Enables CORS
from flask import Flask, render_template



app = create_app()
app.config.from_object(Config)




jwt = JWTManager(app)  # Initializing JWT
CORS(app, supports_credentials=True)  # Enables cookies in CORS

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/")  # <-- Adding route
def home():
    return render_template("auth.html")  # Showing HTML-page

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/products")
def products():
    return render_template("products.html")  # Flask will load a file from templates/

if __name__ == "__main__":
    app.run(debug=True)
