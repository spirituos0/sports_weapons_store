import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:goblin0001@localhost/shop_db"
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # 📌 JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysecretkey")  # Secret key for JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey") # Flask secret
    
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Access token lives for 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 86400  # Refresh token lives for 1 day
    JWT_TOKEN_LOCATION = ["headers", "cookies"]  # Where tokens are stored
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "False") == "True"  # Should be True in production (HTTPS)