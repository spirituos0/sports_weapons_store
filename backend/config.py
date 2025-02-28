import os

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:goblin0001@localhost/shop_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysecretkey")  # Секретный ключ для JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")