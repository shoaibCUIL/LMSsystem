"""
Database Models for LMS System
Complete model definitions with payment and progress tracking
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# ==================== USER MODEL ====================

class User(UserMixin, db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def is_enrolled(self, course_id):
        """Check if user is enrolled in a course"""
        enrollment = Enrollment.query.filter_by(
            user_id=self.id,
            course_id=course_id,
            is_active=True
        ).first()
        
        if not enrollment:
            return False
        
        # Check if enrollment is still valid (not expired)
        if enrollment.is_expired:
            return False
        
        return True
    
    def get_enrollment(self, course_id):
        """Get enrollment for a specific course"""
        return Enrollment.query.filter_by(
            user_id=self.id,
            course_id=course_id
        ).first()
    
    def __repr__(self):
        return f'<User {self.username}>'


# ==================== COURSE MODEL ====================

class Course(db.Model):
    """Course model"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    category = db.Column(db.String(100), nullable=False, index=True)
    level = db.Column(db.String(50), default='Beginner')
    
    price = db.Column(db.Float, default=0.0)
    duration_hours = db.Column(db.Integer, default=0)
    duration_days = db.Column(db.Integer, default=30)
    
    instructor_name = db.Column(db.String(100), nullable=True)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    
    is_published = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lectures = db.relationship('Lecture', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def is_free(self):
        """Check if course is free"""
        return self.price == 0.0
    
    @property
    def lecture_count(self):
        """Get total number of lectures"""
        return self.lectures.count()
    
    @property
    def enrollment_count(self):
        """Get number of enrolled students"""
        return Enrollment.query.filter_by(course_id=self.id, is_active=True).count()
    
    def __repr__(self):
        return f'<Course {self.title}>'


# ==================== LECTURE MODEL ====================

class Lecture(db.Model):
    """Lecture/lesson model"""
    __tablename__ = 'lectures'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(500), nullable=False)
    
    duration_minutes = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)
    
    is_preview = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Lecture {self.title}>'


# ==================== ENROLLMENT MODEL ====================

class Enrollment(db.Model):
    """Enrollment model with payment and progress tracking"""
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    bundle_id = db.Column(db.Integer, db.ForeignKey('bundles.id'), nullable=True)
    
    # Enrollment dates
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Payment tracking
    payment_status = db.Column(db.String(20), default='pending')  # pending, verified, free
    payment_proof_url = db.Column(db.String(500), nullable=True)
    payment_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Progress tracking
    completed_lectures = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, nullable=True)
    
    # Completion
    completed_at = db.Column(db.DateTime, nullable=True)
    certificate_issued = db.Column(db.Boolean, default=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='user_enrollments')
    course = db.relationship('Course', backref='course_enrollments')
    
    @property
    def is_expired(self):
        """Check if enrollment has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def days_remaining(self):
        """Get days remaining before expiration"""
        if not self.expires_at:
            return None
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return delta.days
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        total_lectures = self.course.lecture_count
        if total_lectures == 0:
            return 0
        return min((self.completed_lectures / total_lectures) * 100, 100)
    
    def mark_lecture_complete(self, lecture_id):
        """Mark a lecture as completed"""
        # Check if already completed
        progress = LectureProgress.query.filter_by(
            enrollment_id=self.id,
            lecture_id=lecture_id
        ).first()
        
        if not progress:
            progress = LectureProgress(
                enrollment_id=self.id,
                lecture_id=lecture_id,
                completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
            
            # Update enrollment completed count
            self.completed_lectures += 1
            self.last_accessed = datetime.utcnow()
            
            # Check if course is complete
            if self.progress_percentage >= 100:
                self.completed_at = datetime.utcnow()
            
            db.session.commit()
        
        return progress
    
    def __repr__(self):
        return f'<Enrollment User:{self.user_id} Course:{self.course_id}>'


# ==================== LECTURE PROGRESS MODEL ====================

class LectureProgress(db.Model):
    """Track individual lecture completion"""
    __tablename__ = 'lecture_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'), nullable=False)
    
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    watch_time_seconds = db.Column(db.Integer, default=0)
    
    # Relationships
    enrollment = db.relationship('Enrollment', backref='lecture_progress_records')
    lecture = db.relationship('Lecture', backref='progress_records')
    
    __table_args__ = (
        db.UniqueConstraint('enrollment_id', 'lecture_id', name='unique_enrollment_lecture'),
    )
    
    def __repr__(self):
        return f'<LectureProgress Enrollment:{self.enrollment_id} Lecture:{self.lecture_id}>'


# ==================== BLOG MODEL ====================

class Blog(db.Model):
    """Blog post model"""
    __tablename__ = 'blogs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    
    author = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    
    featured_image_url = db.Column(db.String(500), nullable=True)
    
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime, nullable=True)
    
    views_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def reading_time(self):
        """Estimate reading time in minutes"""
        words = len(self.content.split())
        return max(1, words // 200)
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        db.session.commit()
    
    def __repr__(self):
        return f'<Blog {self.title}>'


# ==================== CUSTOM BUNDLE MODEL ====================

class CustomBundle(db.Model):
    """Custom course bundle model"""
    __tablename__ = 'bundles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    bundle_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    course_ids = db.Column(db.String(500), nullable=False)  # Comma-separated course IDs
    
    total_price = db.Column(db.Float, default=0.0)
    discount_percentage = db.Column(db.Float, default=0.0)
    final_price = db.Column(db.Float, default=0.0)
    
    duration_days = db.Column(db.Integer, default=30)
    
    is_active = db.Column(db.Boolean, default=True)
    activated_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='bundles')
    
    @property
    def course_count(self):
        """Get number of courses in bundle"""
        if not self.course_ids:
            return 0
        return len(self.course_ids.split(','))
    
    @property
    def is_expired(self):
        """Check if bundle has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def get_courses(self):
        """Get all courses in the bundle"""
        if not self.course_ids:
            return []
        
        course_id_list = [int(cid) for cid in self.course_ids.split(',')]
        return Course.query.filter(Course.id.in_(course_id_list)).all()
    
    def calculate_pricing(self):
        """Calculate bundle pricing with discount"""
        courses = self.get_courses()
        
        self.total_price = sum(course.price for course in courses)
        discount_amount = self.total_price * (self.discount_percentage / 100)
        self.final_price = self.total_price - discount_amount
        
        db.session.commit()
    
    def activate_bundle(self):
        """Activate the bundle"""
        from datetime import timedelta
        
        self.is_active = True
        self.activated_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(days=self.duration_days)
        
        db.session.commit()
    
    def __repr__(self):
        return f'<CustomBundle {self.bundle_name}>'


# ==================== EVENT MODEL (OPTIONAL) ====================

class Event(db.Model):
    """Event/webinar model (optional feature)"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    event_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    
    is_published = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Event {self.title}>'


# ==================== TAG MODEL (OPTIONAL) ====================

class Tag(db.Model):
    """Tag model for courses/blogs (optional feature)"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Tag {self.name}>'