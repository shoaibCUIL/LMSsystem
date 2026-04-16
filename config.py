import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret123")

    db_url = os.getenv("DATABASE_URL")

    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///lms.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False