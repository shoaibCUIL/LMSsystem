# ADD/UPDATE THESE FIELDS IN YOUR models.py Enrollment MODEL

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    bundle_id = db.Column(db.Integer, db.ForeignKey('bundles.id'), nullable=True)
    
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # PAYMENT TRACKING
    payment_status = db.Column(db.String(20), default='pending')  # pending, verified, free
    payment_proof_url = db.Column(db.String(500), nullable=True)
    
    # PROGRESS TRACKING
    completed_lectures = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, nullable=True)
    
    completed_at = db.Column(db.DateTime, nullable=True)
    certificate_issued = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')
    
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
        return (self.completed_lectures / total_lectures) * 100
    
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

# ADD THIS NEW MODEL FOR LECTURE PROGRESS TRACKING
class LectureProgress(db.Model):
    __tablename__ = 'lecture_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'), nullable=False)
    
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    watch_time_seconds = db.Column(db.Integer, default=0)
    
    # Relationships
    enrollment = db.relationship('Enrollment', backref='lecture_progress')
    lecture = db.relationship('Lecture', backref='progress_records')
    
    __table_args__ = (
        db.UniqueConstraint('enrollment_id', 'lecture_id', name='unique_enrollment_lecture'),
    )

# UPDATE USER MODEL - ADD THESE METHODS
class User(UserMixin, db.Model):
    # ... existing fields ...
    
    def is_enrolled(self, course_id):
        """Check if user is enrolled in a course"""
        enrollment = Enrollment.query.filter_by(
            user_id=self.id,
            course_id=course_id
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

# UPDATE COURSE MODEL - ADD LECTURE COUNT PROPERTY
class Course(db.Model):
    # ... existing fields ...
    
    @property
    def lecture_count(self):
        """Get total number of lectures"""
        return Lecture.query.filter_by(course_id=self.id).count()
    
    @property
    def enrollment_count(self):
        """Get number of enrolled students"""
        return Enrollment.query.filter_by(course_id=self.id).count()