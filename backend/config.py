import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:goblin0001@localhost/shop_db"
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # 📌 JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysecretkey")  # Секретный ключ для JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey") # Flask secret
    
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Access token живет 1 час
    JWT_REFRESH_TOKEN_EXPIRES = 86400  # Refresh token живет 1 день
    JWT_TOKEN_LOCATION = ["headers", "cookies"]  # Где хранятся токены
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "False") == "True"  # Должно быть True в продакшене (HTTPS)