"""Database instance - prevents circular imports"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()