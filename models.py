from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ================= USER =================
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    custom_bundles = db.relationship('CustomBundle', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


# ================= COURSE =================
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    category = db.Column(db.String(50), nullable=False, index=True)
    level = db.Column(db.String(20), default='Beginner')

    price = db.Column(db.Float, default=0.0)

    duration_hours = db.Column(db.Integer, default=0)
    duration_days = db.Column(db.Integer, default=30)

    # 🔥 IMPORTANT (NEW)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    thumbnail_url = db.Column(db.String(500))
    instructor_name = db.Column(db.String(100))

    is_published = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lectures = db.relationship('Lecture', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def lecture_count(self):
        return self.lectures.count()

    @property
    def enrollment_count(self):
        return self.enrollments.filter_by(is_active=True).count()

    @property
    def is_free(self):
        return self.price == 0


# ================= LECTURE =================
class Lecture(db.Model):
    __tablename__ = 'lectures'

    id = db.Column(db.Integer, primary_key=True)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    video_url = db.Column(db.String(500), nullable=False)

    duration_minutes = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)

    is_preview = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ================= ENROLLMENT =================
class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    progress_percentage = db.Column(db.Float, default=0.0)

    last_accessed = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),
    )

    @property
    def is_expired(self):
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    @property
    def days_remaining(self):
        if self.expires_at:
            return max(0, (self.expires_at - datetime.utcnow()).days)
        return None


# ================= BLOG =================
class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    author = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ================= CUSTOM BUNDLE =================
class CustomBundle(db.Model):
    __tablename__ = 'custom_bundles'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    bundle_name = db.Column(db.String(200), nullable=False)
    course_ids = db.Column(db.String(500), nullable=False)

    duration_days = db.Column(db.Integer, default=30)

    total_price = db.Column(db.Float, default=0.0)
    discount_percentage = db.Column(db.Float, default=0.0)
    final_price = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_courses(self):
        if not self.course_ids:
            return []
        ids = [int(cid) for cid in self.course_ids.split(',')]
        return Course.query.filter(Course.id.in_(ids)).all()

    def calculate_price(self):
        courses = self.get_courses()
        self.total_price = sum(c.price for c in courses)

        discount = self.total_price * (self.discount_percentage / 100)
        self.final_price = self.total_price - discount