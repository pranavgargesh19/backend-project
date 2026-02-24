# app/config.py
import os
import redis

class Config:
    # General Flask Settings
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey123")
    # Database (MySQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:PassWord123!@localhost/user"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email (Flask-Mail)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() in ("true", "1", "t")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") or MAIL_USERNAME
    MAIL_DEBUG = False 

    # Rate Limiting Configuration
    ROUTE_LIMITS = {
        "/users/login": {"limit": 5, "window_seconds": 60},
        "/users/forgot-password": {"limit": 3, "window_seconds": 3600},
        "/users/reset-password": {"limit": 3, "window_seconds": 3600},
        "/users/": {
            "POST": {"limit": 10, "window_seconds": 3600},
            "GET": {"limit": 30, "window_seconds": 60},
        },
        "/users/<id>": {
            "GET": {"limit": 60, "window_seconds": 60},
            "PUT": {"limit": 20, "window_seconds": 60},
            "DELETE": {"limit": 5, "window_seconds": 60},
        },
        "/users/refresh": {"limit": 20, "window_seconds": 60},
        "/users/logout": {"limit": 20, "window_seconds": 60},
    }
    