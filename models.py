from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Extended registration fields
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)  # Student/Professional/Faculty/etc
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    education = db.Column(db.String(200), nullable=False)  # Highest qualification
    university = db.Column(db.String(200), nullable=False)
    
    # Account metadata
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    detailed_description = db.Column(db.Text)
    
    # Pricing structure (PKR base)
    price_per_day = db.Column(db.Float, default=75.0)  # Base: 1500 PKR / 20 days = 75 PKR/day
    min_days = db.Column(db.Integer, default=2)
    min_price_pkr = db.Column(db.Float, default=1500.0)
    
    # Course metadata
    thumbnail = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    level = db.Column(db.String(50))  # Beginner/Intermediate/Advanced
    duration_estimate = db.Column(db.String(100))  # "6 weeks", "3 months", etc
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lectures = db.relationship('Lecture', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def calculate_price(self, days=None, months=None, weeks=None):
        """Calculate price based on duration"""
        if months:
            total_days = months * 30
        elif weeks:
            total_days = weeks * 7
        elif days:
            total_days = days
        else:
            total_days = self.min_days
        
        # Ensure minimum days
        total_days = max(total_days, self.min_days)
        
        # Calculate price
        calculated_price = total_days * self.price_per_day
        
        # Ensure minimum price
        return max(calculated_price, self.min_price_pkr)
    
    def calculate_days(self, price_pkr):
        """Calculate days based on price"""
        days = int(price_pkr / self.price_per_day)
        return max(days, self.min_days)
    
    def __repr__(self):
        return f'<Course {self.title}>'


class Lecture(db.Model):
    __tablename__ = 'lectures'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # HTML content
    video_url = db.Column(db.String(500))
    order_number = db.Column(db.Integer, default=0)
    
    is_free = db.Column(db.Boolean, default=False)  # Free preview lectures
    duration_minutes = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Lecture {self.title}>'


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Enrollment details
    enrollment_type = db.Column(db.String(20))  # 'days', 'weeks', 'months'
    duration_value = db.Column(db.Integer)  # Number of days/weeks/months
    total_days = db.Column(db.Integer, nullable=False)
    
    # Payment information
    price_paid_pkr = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='PKR')
    payment_method = db.Column(db.String(50), nullable=False)  # JazzCash/Easypaisa/Bank
    payment_receipt = db.Column(db.String(500), nullable=False)  # Receipt file path
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')  # pending/approved/rejected/expired
    admin_notes = db.Column(db.Text)
    
    # Dates
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Index for faster queries
    __table_args__ = (
        db.Index('idx_user_course', 'user_id', 'course_id'),
        db.Index('idx_status', 'status'),
    )
    
    def is_active(self):
        """Check if enrollment is active"""
        if self.status != 'approved':
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def __repr__(self):
        return f'<Enrollment User:{self.user_id} Course:{self.course_id}>'


class Blog(db.Model):
    __tablename__ = 'blogs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    thumbnail = db.Column(db.String(500))
    author = db.Column(db.String(100))
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Blog {self.title}>'


class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Event {self.title}>'


class CustomBundle(db.Model):
    __tablename__ = 'custom_bundles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CustomBundle {self.name}>'


class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Tag {self.name}>'