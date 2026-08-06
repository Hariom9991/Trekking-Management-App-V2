import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///trekking.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = os.getenv('CACHE_TYPE', 'RedisCache')
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 120

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'Asia/Kolkata')

    GOOGLE_CHAT_WEBHOOK = os.getenv('GOOGLE_CHAT_WEBHOOK', '')

    # Mailpit: default SMTP on localhost:1025, no TLS, no auth
    SMTP_HOST = os.getenv('SMTP_HOST', '127.0.0.1')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '1025'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_SENDER = os.getenv('SMTP_SENDER', 'admin@tma.com')
    SMTP_USE_TLS = False

    SESSION_COOKIE_NAME = 'tma_session'
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = False