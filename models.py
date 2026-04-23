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
    
    # New hourly-based pricing structure
    level = db.Column(db.String(50), default='beginner')  # 'beginner', 'intermediate', 'advanced'
    hourly_rate_pkr = db.Column(db.Integer, default=800)  # PKR per hour
    hourly_rate_usd = db.Column(db.Integer, default=6)    # USD per hour
    
    # Course metadata
    thumbnail = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    duration_estimate = db.Column(db.String(100))  # "6 weeks", "3 months", etc
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lectures = db.relationship('Lecture', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_package_price(self, package_type, currency='pkr'):
        """Get price for daily/weekly/monthly package"""
        from flask import current_app
        pricing = current_app.config['PACKAGE_PRICING']
        
        if package_type not in pricing:
            return 0
        
        package = pricing[package_type]
        level_pricing = package.get(self.level, {})
        
        return level_pricing.get(currency, 0)
    
    def get_level_price(self, level, days, country='Pakistan'):
        """Calculate price based on level, days, and country"""
        base_rates = {
            'beginner': 250,
            'intermediate': 350,
            'advanced': 500
        }
        
        rate = base_rates.get(level.lower(), 250)
        base_price = rate * days
        
        # Apply tiered discount
        if days >= 10:
            discount = 0.15
        elif days >= 5:
            discount = 0.10
        elif days >= 3:
            discount = 0.05
        else:
            discount = 0
        
        final_price = base_price * (1 - discount)
        
        # Double for international
        if country != 'Pakistan':
            final_price *= 2
        
        return {
            'base_price': base_price,
            'discount_percent': int(discount * 100),
            'discount_amount': base_price * discount,
            'final_price': round(final_price),
            'rate_per_day': rate
        }

    def calculate_custom_price(self, hours, currency='pkr'):
        """Calculate price for custom number of hours"""
        if currency == 'pkr':
            return self.hourly_rate_pkr * hours
        else:
            return self.hourly_rate_usd * hours
    
    def get_currency(self, country):
        """Determine currency based on country"""
        return 'pkr' if country == 'Pakistan' else 'usd'
    
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
    

# ================================
# DISCUSSION MODELS
# ================================

class DiscussionRoom(db.Model):
    __tablename__ = 'discussion_rooms'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', backref='discussion_room', uselist=False)
    sessions = db.relationship('DiscussionSession', backref='room',
                               lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('DiscussionMessage', backref='room',
                               lazy='dynamic', cascade='all, delete-orphan')
    subscriptions = db.relationship('DiscussionSubscription', backref='room',
                                    lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<DiscussionRoom {self.title}>'


class DiscussionSession(db.Model):
    __tablename__ = 'discussion_sessions'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('discussion_rooms.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    topic = db.Column(db.String(300))

    # Scheduling
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)

    # Meeting link (Zoom/Meet/Teams)
    meeting_link = db.Column(db.String(500))
    meeting_password = db.Column(db.String(100))
    meeting_platform = db.Column(db.String(50), default='Zoom')  # Zoom/Meet/Teams

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_upcoming(self):
        return self.scheduled_at > datetime.utcnow()

    def is_live(self):
        from datetime import timedelta
        end_time = self.scheduled_at + timedelta(minutes=self.duration_minutes)
        return self.scheduled_at <= datetime.utcnow() <= end_time

    def __repr__(self):
        return f'<DiscussionSession {self.title}>'


class DiscussionSubscription(db.Model):
    __tablename__ = 'discussion_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('discussion_rooms.id'), nullable=False)

    # Flexible pricing: user picks topic/hours/days
    topic = db.Column(db.String(300), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)   # total days
    hours_per_day = db.Column(db.Integer, nullable=False)   # hours per day
    total_hours = db.Column(db.Integer, nullable=False)     # duration_days * hours_per_day

    # Pricing (calculated based on topic complexity + hours)
    price_per_hour = db.Column(db.Integer, nullable=False)  # PKR per hour
    total_price = db.Column(db.Float, nullable=False)

    # Payment
    payment_method = db.Column(db.String(50), nullable=False)
    payment_receipt = db.Column(db.String(500), nullable=False)

    # Status
    status = db.Column(db.String(20), default='pending')  # pending/approved/rejected/expired
    admin_notes = db.Column(db.Text)

    # Dates
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='discussion_subscriptions')

    def is_active(self):
        if self.status != 'approved':
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def __repr__(self):
        return f'<DiscussionSubscription User:{self.user_id} Room:{self.room_id}>'


class DiscussionMessage(db.Model):
    __tablename__ = 'discussion_messages'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('discussion_rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('discussion_sessions.id'), nullable=True)

    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship('User', backref='discussion_messages')
    session = db.relationship('DiscussionSession', backref='messages')

    def __repr__(self):
        return f'<DiscussionMessage User:{self.user_id} Room:{self.room_id}>'