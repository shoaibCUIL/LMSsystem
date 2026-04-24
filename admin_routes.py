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
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_enrollments = Enrollment.query.count()
    pending_count = Enrollment.query.filter_by(status='pending').count()

    # Last 10 enrollments for the "Recent Activity" table
    recent_enrollments = Enrollment.query.order_by(
        Enrollment.enrolled_at.desc()
    ).limit(10).all()

    # ALL pending enrollments — no limit — shown in the dedicated section
    pending_enrollments_list = Enrollment.query.filter_by(
        status='pending'
    ).order_by(Enrollment.enrolled_at.desc()).all()

    active_enrollments = Enrollment.query.filter_by(status='approved').all()
    active_count = sum(1 for e in active_enrollments if e.is_active())

    stats = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'pending_enrollments': pending_count,
        'active_count': active_count,
    }

    return render_template(
        'admin/admin.html',
        stats=stats,
        recent_enrollments=recent_enrollments,
        pending_enrollments_list=pending_enrollments_list,
    )


# ================================
# ENROLLMENT MANAGEMENT
# ================================

@admin_bp.route('/enrollments')
@login_required
@admin_required
def enrollments():
    status_filter = request.args.get('status', 'all')
    query = Enrollment.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    enrollments = query.order_by(Enrollment.enrolled_at.desc()).all()
    return render_template('admin/enrollments.html',
                           enrollments=enrollments,
                           status_filter=status_filter)

@admin_bp.route('/debug-enrollments')
@login_required
@admin_required
def debug_enrollments():
    all_e = Enrollment.query.all()
    result = [f"ID:{e.id} status='{e.status}' user={e.student.email} course={e.course.title}" for e in all_e]
    return '<br>'.join(result) if result else 'No enrollments found in database at all'

@admin_bp.route('/enrollments/<int:enrollment_id>')
@login_required
@admin_required
def enrollment_detail(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    return render_template('admin/enrollment_detail.html', enrollment=enrollment)


@admin_bp.route('/enrollments/<int:enrollment_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    if enrollment.status != 'pending':
        flash('This enrollment is not pending approval.', 'warning')
        return redirect(url_for('admin.enrollment_detail', enrollment_id=enrollment_id))

    try:
        approved_at, expires_at = calculate_enrollment_dates(enrollment.total_days)
        enrollment.status = 'approved'
        enrollment.approved_at = approved_at
        enrollment.expires_at = expires_at
        db.session.commit()
        current_app.logger.info(
            f'Enrollment approved: ID={enrollment_id} by Admin={current_user.id}'
        )
        flash('Enrollment approved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error approving enrollment: {str(e)}')
        flash('An error occurred while approving the enrollment.', 'danger')

    return redirect(url_for('admin.enrollment_detail', enrollment_id=enrollment_id))


@admin_bp.route('/enrollments/<int:enrollment_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    if enrollment.status != 'pending':
        flash('This enrollment is not pending.', 'warning')
        return redirect(url_for('admin.enrollment_detail', enrollment_id=enrollment_id))

    try:
        admin_notes = request.form.get('admin_notes', '')
        enrollment.status = 'rejected'
        enrollment.admin_notes = admin_notes
        db.session.commit()
        current_app.logger.info(
            f'Enrollment rejected: ID={enrollment_id} by Admin={current_user.id}'
        )
        flash('Enrollment rejected.', 'info')
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
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=courses)


@admin_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_course():
    form = CourseForm()

    if form.validate_on_submit():
        try:
            slug = slugify(form.title.data)
            existing = Course.query.filter_by(slug=slug).first()
            if existing:
                slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d')}"

            thumbnail_filename = None
            if form.thumbnail.data:
                thumbnail_filename = save_thumbnail(form.thumbnail.data)

            course = Course(
                title=form.title.data,
                slug=slug,
                description=form.description.data,
                detailed_description=form.detailed_description.data,
                level=form.level.data,
                duration_estimate=form.duration_estimate.data,
                hourly_rate_pkr=form.hourly_rate_pkr.data,
                hourly_rate_usd=form.hourly_rate_usd.data,
                thumbnail=thumbnail_filename,
                is_active=form.is_active.data
            )

            db.session.add(course)
            db.session.commit()
            current_app.logger.info(
                f'Course created: {course.title} by Admin={current_user.id}'
            )
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
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)

    if form.validate_on_submit():
        try:
            course.title = form.title.data
            course.description = form.description.data
            course.detailed_description = form.detailed_description.data
            course.level = form.level.data
            course.duration_estimate = form.duration_estimate.data
            course.hourly_rate_pkr = form.hourly_rate_pkr.data
            course.hourly_rate_usd = form.hourly_rate_usd.data
            course.is_active = form.is_active.data

            if form.thumbnail.data:
                thumbnail_filename = save_thumbnail(form.thumbnail.data)
                if thumbnail_filename:
                    course.thumbnail = thumbnail_filename

            db.session.commit()
            current_app.logger.info(
                f'Course updated: {course.title} by Admin={current_user.id}'
            )
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
    course = Course.query.get_or_404(course_id)
    try:
        db.session.delete(course)
        db.session.commit()
        current_app.logger.info(
            f'Course deleted: {course.title} by Admin={current_user.id}'
        )
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
    course = Course.query.get_or_404(course_id)
    lectures = course.lectures.order_by(Lecture.order_number).all()
    return render_template('admin/lectures.html', course=course, lectures=lectures)


@admin_bp.route('/courses/<int:course_id>/lectures/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_lecture(course_id):
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
            current_app.logger.info(
                f'Lecture created: {lecture.title} for Course={course.id}'
            )
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

    return render_template('admin/lecture_form.html', form=form, lecture=lecture,
                           course=course, title='Edit Lecture')


@admin_bp.route('/lectures/<int:lecture_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_lecture(lecture_id):
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
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot change your own admin status.', 'warning')
        return redirect(url_for('admin.users'))

    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = 'granted' if user.is_admin else 'revoked'
        current_app.logger.info(
            f'Admin privileges {status} for user: {user.email}'
        )
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


# ================================
# DISCUSSION MANAGEMENT
# ================================

@admin_bp.route('/discussion/rooms')
@login_required
@admin_required
def discussion_rooms():
    from models import DiscussionRoom
    rooms = DiscussionRoom.query.order_by(DiscussionRoom.created_at.desc()).all()
    return render_template('admin/discussion_rooms.html', rooms=rooms)


@admin_bp.route('/discussion/rooms/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_discussion_room():
    from models import DiscussionRoom
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        course_id = request.form.get('course_id') or None
        if not title:
            flash('Title is required.', 'danger')
        else:
            room = DiscussionRoom(
                title=title,
                description=description,
                course_id=course_id
            )
            db.session.add(room)
            db.session.commit()
            flash('Discussion room created!', 'success')
            return redirect(url_for('admin.discussion_rooms'))
    courses = Course.query.filter_by(is_active=True).all()
    return render_template('admin/create_discussion_room.html', courses=courses)


@admin_bp.route('/discussion/sessions')
@login_required
@admin_required
def discussion_sessions():
    from models import DiscussionSession, DiscussionRoom
    sessions = DiscussionSession.query.order_by(
        DiscussionSession.scheduled_at.desc()
    ).all()
    rooms = DiscussionRoom.query.filter_by(is_active=True).all()
    return render_template('admin/discussion_sessions.html',
                           sessions=sessions, rooms=rooms)


@admin_bp.route('/discussion/sessions/create', methods=['POST'])
@login_required
@admin_required
def create_discussion_session():
    from models import DiscussionSession
    try:
        scheduled_str = request.form.get('scheduled_at', '')
        scheduled_at = datetime.strptime(scheduled_str, '%Y-%m-%dT%H:%M')

        session = DiscussionSession(
            room_id=int(request.form.get('room_id')),
            title=request.form.get('title', '').strip(),
            description=request.form.get('description', '').strip(),
            topic=request.form.get('topic', '').strip(),
            scheduled_at=scheduled_at,
            duration_minutes=int(request.form.get('duration_minutes', 60)),
            meeting_link=request.form.get('meeting_link', '').strip(),
            meeting_password=request.form.get('meeting_password', '').strip(),
            meeting_platform=request.form.get('meeting_platform', 'Zoom')
        )
        db.session.add(session)
        db.session.commit()
        flash('Session scheduled successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('admin.discussion_sessions'))


@admin_bp.route('/discussion/sessions/<int:session_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_discussion_session(session_id):
    from models import DiscussionSession
    s = DiscussionSession.query.get_or_404(session_id)
    db.session.delete(s)
    db.session.commit()
    flash('Session deleted.', 'info')
    return redirect(url_for('admin.discussion_sessions'))


@admin_bp.route('/discussion/subscriptions')
@login_required
@admin_required
def discussion_subscriptions():
    from models import DiscussionSubscription
    status_filter = request.args.get('status', 'all')
    query = DiscussionSubscription.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    subs = query.order_by(DiscussionSubscription.subscribed_at.desc()).all()
    return render_template('admin/discussion_subscriptions.html',
                           subscriptions=subs, status_filter=status_filter)


@admin_bp.route('/discussion/subscriptions/<int:sub_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_discussion_sub(sub_id):
    from models import DiscussionSubscription
    sub = DiscussionSubscription.query.get_or_404(sub_id)
    if sub.status != 'pending':
        flash('Not pending.', 'warning')
        return redirect(url_for('admin.discussion_subscriptions'))
    sub.status = 'approved'
    sub.approved_at = datetime.utcnow()
    sub.expires_at = datetime.utcnow() + timedelta(days=sub.duration_days)
    db.session.commit()
    flash(f'Subscription approved for {sub.user.first_name}!', 'success')
    return redirect(url_for('admin.discussion_subscriptions'))


@admin_bp.route('/discussion/subscriptions/<int:sub_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_discussion_sub(sub_id):
    from models import DiscussionSubscription
    sub = DiscussionSubscription.query.get_or_404(sub_id)
    sub.status = 'rejected'
    sub.admin_notes = request.form.get('admin_notes', '')
    db.session.commit()
    flash('Subscription rejected.', 'info')
    return redirect(url_for('admin.discussion_subscriptions'))


@admin_bp.route('/discussion/rooms/<int:room_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_discussion_room(room_id):
    from models import DiscussionRoom
    room = DiscussionRoom.query.get_or_404(room_id)
    room.is_active = not room.is_active
    db.session.commit()
    status = 'activated' if room.is_active else 'deactivated'
    flash(f'Room "{room.title}" {status}.', 'success')
    return redirect(url_for('admin.discussion_rooms'))