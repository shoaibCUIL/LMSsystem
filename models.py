from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ================= USER =================
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship('Enrollment', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.username


# ================= COURSE =================
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    category = db.Column(db.String(50))
    level = db.Column(db.String(20), default="Beginner")

    price = db.Column(db.Float, default=0)

    duration_days = db.Column(db.Integer, default=30)
    duration_hours = db.Column(db.Integer, default=0)

    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    instructor_name = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lectures = db.relationship('Lecture', backref='course', lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)


# ================= LECTURE =================
class Lecture(db.Model):
    __tablename__ = 'lectures'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    title = db.Column(db.String(200))
    video_url = db.Column(db.String(500))


# ================= ENROLLMENT =================
class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)


# ================= BLOG =================
class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ================= CUSTOM BUNDLE =================
class CustomBundle(db.Model):
    __tablename__ = 'custom_bundles'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    bundle_name = db.Column(db.String(200))
    course_ids = db.Column(db.String(200))  # "1,2,3"

    total_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)