import os


class Config:
    # ================= SECRET KEY =================
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")


    # ================= DATABASE =================
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # Fix for Railway / Heroku postgres URL
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local development fallback
        SQLALCHEMY_DATABASE_URI = "sqlite:///lms.db"


    # ================= SQLALCHEMY =================
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # ================= OPTIONAL SETTINGS =================
    # (for future features)

    # Upload folder (for course thumbnails later)
    UPLOAD_FOLDER = "static/uploads"

    # Max upload size (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


    # ================= DEBUG MODE =================
    DEBUG = True