from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta

db = SQLAlchemy()


# ================= USER =================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)

    # Global access expiry (optional)
    expiry_date = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow() + timedelta(days=7)
    )

    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)


# ================= COURSE =================
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    price = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(100), default="General")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    lectures = db.relationship('Lecture', backref='course', lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)


# ================= LECTURE =================
class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    video_url = db.Column(db.Text, nullable=False)

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('course.id'),
        nullable=False
    )


# ================= ENROLLMENT =================
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('course.id'),
        nullable=False
    )

    enrolled_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Per-course expiry (important for LMS)
    expiry_date = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow() + timedelta(days=30)
    )


# ================= BLOG =================
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    author = db.Column(db.String(100), default="Admin")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ================= EVENT =================
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    date = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)