from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta

db = SQLAlchemy()

# ------------------ USER ------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)

    # Access expiry (7 days default)
    expiry_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))


# ------------------ COURSE ------------------

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)

    lectures = db.relationship('Lecture', backref='course', lazy=True)


# ------------------ LECTURE ------------------

class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    video_url = db.Column(db.Text)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)