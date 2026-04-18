"""
Database Models for LMS System
Complete production-ready models with relationships and validations
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
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
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def get_enrolled_courses(self):
        """Get all active enrolled courses"""
        active_enrollments = Enrollment.query.filter_by(
            user_id=self.id,
            is_active=True
        ).all()
        return [e.course for e in active_enrollments]
    
    def is_enrolled(self, course_id):
        """Check if user is enrolled in a course"""
        enrollment = Enrollment.query.filter_by(
            user_id=self.id,
            course_id=course_id,
            is_active=True
        ).first()
        return enrollment is not None
    
    @property
    def full_name(self):
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        return f'<User {self.username}>'


class Course(db.Model):
    """Course model with complete metadata"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    level = db.Column(db.String(20), default='Beginner')  # Beginner, Intermediate, Advanced
    price = db.Column(db.Float, default=0.0)
    duration_hours = db.Column(db.Integer, default=0)
    duration_days = db.Column(db.Integer, default=30)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)  # Recommended completion time in days
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
        """Get total number of lectures"""
        return self.lectures.count()
    
    @property
    def enrollment_count(self):
        """Get total enrollments"""
        return self.enrollments.filter_by(is_active=True).count()
    
    @property
    def is_free(self):
        """Check if course is free"""
        return self.price == 0
    
    def __repr__(self):
        return f'<Course {self.title}>'


class Lecture(db.Model):
    """Lecture/Lesson model for course content"""
    __tablename__ = 'lectures'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500), nullable=False)
    duration_minutes = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)
    is_preview = db.Column(db.Boolean, default=False)  # Preview available without enrollment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Lecture {self.title}>'


class Enrollment(db.Model):
    """Enrollment model tracking user course access"""
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
    
    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),
    )
    
    @property
    def is_expired(self):
        """Check if enrollment has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    @property
    def days_remaining(self):
        """Get days remaining until expiry"""
        if self.expires_at:
            delta = self.expires_at - datetime.utcnow()
            return max(0, delta.days)
        return None
    
    def __repr__(self):
        return f'<Enrollment User:{self.user_id} Course:{self.course_id}>'


class Blog(db.Model):
    """Blog/Article model for content marketing"""
    __tablename__ = 'blogs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500))
    author = db.Column(db.String(100))
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))  # Comma-separated
    featured_image = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True)
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        db.session.commit()
    
    @property
    def reading_time(self):
        """Calculate estimated reading time in minutes"""
        words = len(self.content.split())
        return max(1, round(words / 200))  # Average reading speed: 200 WPM
    
    def __repr__(self):
        return f'<Blog {self.title}>'


class Event(db.Model):
    """Event model for webinars, workshops, etc."""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50))  # Webinar, Workshop, Conference
    location = db.Column(db.String(200))  # Online/Physical address
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    max_participants = db.Column(db.Integer)
    registration_deadline = db.Column(db.DateTime)
    is_free = db.Column(db.Boolean, default=True)
    price = db.Column(db.Float, default=0.0)
    instructor_name = db.Column(db.String(100))
    meeting_link = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_upcoming(self):
        """Check if event is in the future"""
        return datetime.utcnow() < self.start_time
    
    @property
    def is_past(self):
        """Check if event has ended"""
        if self.end_time:
            return datetime.utcnow() > self.end_time
        return datetime.utcnow() > self.start_time
    
    def __repr__(self):
        return f'<Event {self.title}>'


class CustomBundle(db.Model):
    """Custom course bundle created by users"""
    __tablename__ = 'custom_bundles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bundle_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    course_ids = db.Column(db.String(500), nullable=False)  # Comma-separated course IDs
    duration_days = db.Column(db.Integer, default=30)
    total_price = db.Column(db.Float, default=0.0)
    discount_percentage = db.Column(db.Float, default=0.0)
    final_price = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    def get_courses(self):
        """Get list of Course objects in this bundle"""
        if not self.course_ids:
            return []
        course_id_list = [int(cid) for cid in self.course_ids.split(',') if cid.strip()]
        return Course.query.filter(Course.id.in_(course_id_list)).all()
    
    def calculate_pricing(self):
        """Calculate bundle pricing with discount"""
        courses = self.get_courses()
        self.total_price = sum(course.price for course in courses)
        
        # Apply discount
        discount_amount = self.total_price * (self.discount_percentage / 100)
        self.final_price = self.total_price - discount_amount
        
        return self.final_price
    
    def activate_bundle(self):
        """Activate bundle and set expiry"""
        self.is_active = True
        self.activated_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(days=self.duration_days)
        db.session.commit()
    
    @property
    def is_expired(self):
        """Check if bundle has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    @property
    def course_count(self):
        """Get number of courses in bundle"""
        if not self.course_ids:
            return 0
        return len([cid for cid in self.course_ids.split(',') if cid.strip()])
    
    def __repr__(self):
        return f'<CustomBundle {self.bundle_name}>'


# Association table for many-to-many relationships (if needed in future)
course_tags = db.Table('course_tags',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Tag(db.Model):
    """Tag model for categorization"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Tag {self.name}>'