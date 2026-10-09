import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "resumes")

os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(INSTANCE_DIR, "ppa.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = UPLOAD_DIR
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB resumes


    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = 60  # seconds - cache expiry

    
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    GCHAT_WEBHOOK_URL = os.environ.get("GCHAT_WEBHOOK_URL", "")
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@ppa.local")

    ADMIN_NAME = os.environ.get("ADMIN_NAME", "Placement Admin")
    ADMIN_LOGIN_EMAIL = os.environ.get("ADMIN_LOGIN_EMAIL", "admin@ppa.local")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")
