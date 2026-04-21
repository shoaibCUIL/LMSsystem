from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from database import db
from models import User, Course, Enrollment, Lecture, Blog, Event
from forms import CourseForm, LectureForm
from utils import save_thumbnail, slugify, calculate_enrollment_dates

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


# ================================
# ADMIN DASHBOARD
# ================================

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    # Statistics
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_enrollments = Enrollment.query.count()
    
    # Pending enrollments
    pending_enrollments = Enrollment.query.filter_by(status='pending').count()
    
    # Recent enrollments
    recent_enrollments = Enrollment.query.order_by(
        Enrollment.enrolled_at.desc()
    ).limit(10).all()
    
    # Active enrollments
    active_enrollments = Enrollment.query.filter_by(status='approved').all()
    active_count = sum(1 for e in active_enrollments if e.is_active())
    
    return render_template('admin/admin.html',
                          total_users=total_users,
                          total_courses=total_courses,
                          total_enrollments=total_enrollments,
                          pending_enrollments=pending_enrollments,
                          active_count=active_count,
                          recent_enrollments=recent_enrollments)


# ================================
# ENROLLMENT MANAGEMENT
# ================================

@admin_bp.route('/enrollments')
@login_required
@admin_required
def enrollments():
    """Manage all enrollments"""
    status_filter = request.args.get('status', 'all')
    
    query = Enrollment.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    enrollments = query.order_by(Enrollment.enrolled_at.desc()).all()
    
    return render_template('admin/enrollments.html',
                          enrollments=enrollments,
                          status_filter=status_filter)


@admin_bp.route('/enrollments/<int:enrollment_id>')
@login_required
@admin_required
def enrollment_detail(enrollment_id):
    """View enrollment details"""
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    return render_template('admin/enrollment_detail.html', enrollment=enrollment)


@admin_bp.route('/enrollments/<int:enrollment_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_enrollment(enrollment_id):
    """Approve an enrollment"""
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    if enrollment.status != 'pending':
        flash('This enrollment is not pending approval.', 'warning')
        return redirect(url_for('admin.enrollment_detail', enrollment_id=enrollment_id))
    
    try:
        # Calculate expiry date
        approved_at, expires_at = calculate_enrollment_dates(enrollment.total_days)
        
        # Update enrollment
        enrollment.status = 'approved'
        enrollment.approved_at = approved_at
        enrollment.expires_at = expires_at
        
        db.session.commit()
        
        current_app.logger.info(f'Enrollment approved: ID={enrollment_id} by Admin={current_user.id}')
        flash('Enrollment approved successfully!', 'success')
        
        # TODO: Send email notification to user
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error approving enrollment: {str(e)}')
        flash('An error occurred while approving the enrollment.', 'danger')
    
    return redirect(url_for('admin.enrollment_detail', enrollment_id=enrollment_id))


@admin_bp.route('/enrollments/<int:enrollment_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_enrollment(enrollment_id):
    """Reject an enrollment"""
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    if enrollment.status != 'pending':
        flash('This enrollment is not pending.', 'warning')
        return redirect(url_for('admin.enrollment_detail', enrollment_id=enrollment_id))
    
    try:
        admin_notes = request.form.get('admin_notes', '')
        
        enrollment.status = 'rejected'
        enrollment.admin_notes = admin_notes
        
        db.session.commit()
        
        current_app.logger.info(f'Enrollment rejected: ID={enrollment_id} by Admin={current_user.id}')
        flash('Enrollment rejected.', 'info')
        
        # TODO: Send email notification to user
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error rejecting enrollment: {str(e)}')
        flash('An error occurred while rejecting the enrollment.', 'danger')
    
    return redirect(url_for('admin.enrollment_detail', enrollment_id=enrollment_id))


# ================================
# COURSE MANAGEMENT
# ================================

@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    """Manage courses"""
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=courses)


@admin_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_course():
    """Create new course"""
    form = CourseForm()
    
    if form.validate_on_submit():
        try:
            # Generate slug from title
            slug = slugify(form.title.data)
            
            # Check if slug exists
            existing = Course.query.filter_by(slug=slug).first()
            if existing:
                slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d')}"
            
            # Save thumbnail if provided
            thumbnail_filename = None
            if form.thumbnail.data:
                thumbnail_filename = save_thumbnail(form.thumbnail.data)
            
            # Create course
            course = Course(
                title=form.title.data,
                slug=slug,
                description=form.description.data,
                detailed_description=form.detailed_description.data,
                level=form.level.data,
                duration_estimate=form.duration_estimate.data,
                price_per_day=form.price_per_day.data,
                min_days=form.min_days.data,
                min_price_pkr=form.min_price_pkr.data,
                thumbnail=thumbnail_filename,
                is_active=form.is_active.data
            )
            
            db.session.add(course)
            db.session.commit()
            
            current_app.logger.info(f'Course created: {course.title} by Admin={current_user.id}')
            flash('Course created successfully!', 'success')
            return redirect(url_for('admin.courses'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating course: {str(e)}')
            flash('An error occurred while creating the course.', 'danger')
    
    return render_template('admin/course_form.html', form=form, title='Create Course')


@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    """Edit course"""
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    
    if form.validate_on_submit():
        try:
            course.title = form.title.data
            course.description = form.description.data
            course.detailed_description = form.detailed_description.data
            course.level = form.level.data
            course.duration_estimate = form.duration_estimate.data
            course.price_per_day = form.price_per_day.data
            course.min_days = form.min_days.data
            course.min_price_pkr = form.min_price_pkr.data
            course.is_active = form.is_active.data
            
            # Update thumbnail if provided
            if form.thumbnail.data:
                thumbnail_filename = save_thumbnail(form.thumbnail.data)
                if thumbnail_filename:
                    course.thumbnail = thumbnail_filename
            
            db.session.commit()
            
            current_app.logger.info(f'Course updated: {course.title} by Admin={current_user.id}')
            flash('Course updated successfully!', 'success')
            return redirect(url_for('admin.courses'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating course: {str(e)}')
            flash('An error occurred while updating the course.', 'danger')
    
    return render_template('admin/course_form.html', form=form, course=course, title='Edit Course')


@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    """Delete course"""
    course = Course.query.get_or_404(course_id)
    
    try:
        db.session.delete(course)
        db.session.commit()
        
        current_app.logger.info(f'Course deleted: {course.title} by Admin={current_user.id}')
        flash('Course deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting course: {str(e)}')
        flash('An error occurred while deleting the course.', 'danger')
    
    return redirect(url_for('admin.courses'))


# ================================
# LECTURE MANAGEMENT
# ================================

@admin_bp.route('/courses/<int:course_id>/lectures')
@login_required
@admin_required
def course_lectures(course_id):
    """Manage course lectures"""
    course = Course.query.get_or_404(course_id)
    lectures = course.lectures.order_by(Lecture.order_number).all()
    return render_template('admin/lectures.html', course=course, lectures=lectures)


@admin_bp.route('/courses/<int:course_id>/lectures/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_lecture(course_id):
    """Create lecture"""
    course = Course.query.get_or_404(course_id)
    form = LectureForm()
    
    if form.validate_on_submit():
        try:
            lecture = Lecture(
                course_id=course.id,
                title=form.title.data,
                description=form.description.data,
                content=form.content.data,
                video_url=form.video_url.data,
                order_number=form.order_number.data,
                is_free=form.is_free.data,
                duration_minutes=form.duration_minutes.data
            )
            
            db.session.add(lecture)
            db.session.commit()
            
            current_app.logger.info(f'Lecture created: {lecture.title} for Course={course.id}')
            flash('Lecture created successfully!', 'success')
            return redirect(url_for('admin.course_lectures', course_id=course.id))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating lecture: {str(e)}')
            flash('An error occurred while creating the lecture.', 'danger')
    
    return render_template('admin/lecture_form.html', form=form, course=course, title='Create Lecture')


@admin_bp.route('/lectures/<int:lecture_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lecture(lecture_id):
    """Edit lecture"""
    lecture = Lecture.query.get_or_404(lecture_id)
    course = lecture.course
    form = LectureForm(obj=lecture)
    
    if form.validate_on_submit():
        try:
            lecture.title = form.title.data
            lecture.description = form.description.data
            lecture.content = form.content.data
            lecture.video_url = form.video_url.data
            lecture.order_number = form.order_number.data
            lecture.is_free = form.is_free.data
            lecture.duration_minutes = form.duration_minutes.data
            
            db.session.commit()
            
            current_app.logger.info(f'Lecture updated: {lecture.title}')
            flash('Lecture updated successfully!', 'success')
            return redirect(url_for('admin.course_lectures', course_id=course.id))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating lecture: {str(e)}')
            flash('An error occurred while updating the lecture.', 'danger')
    
    return render_template('admin/lecture_form.html', form=form, lecture=lecture, course=course, title='Edit Lecture')


@admin_bp.route('/lectures/<int:lecture_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_lecture(lecture_id):
    """Delete lecture"""
    lecture = Lecture.query.get_or_404(lecture_id)
    course_id = lecture.course_id
    
    try:
        db.session.delete(lecture)
        db.session.commit()
        
        current_app.logger.info(f'Lecture deleted: {lecture.title}')
        flash('Lecture deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting lecture: {str(e)}')
        flash('An error occurred while deleting the lecture.', 'danger')
    
    return redirect(url_for('admin.course_lectures', course_id=course_id))


# ================================
# USER MANAGEMENT
# ================================

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle user admin status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot change your own admin status.', 'warning')
        return redirect(url_for('admin.users'))
    
    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = 'granted' if user.is_admin else 'revoked'
        current_app.logger.info(f'Admin privileges {status} for user: {user.email}')
        flash(f'Admin privileges {status} for {user.email}', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error toggling admin status: {str(e)}')
        flash('An error occurred.', 'danger')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin.users'))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        current_app.logger.info(f'User {status}: {user.email}')
        flash(f'User {user.email} {status}', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error toggling user status: {str(e)}')
        flash('An error occurred.', 'danger')
    
    return redirect(url_for('admin.users'))