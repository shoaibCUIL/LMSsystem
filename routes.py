from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, send_file
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from datetime import datetime, timedelta
from database import db
from models import User, Course, Enrollment, Lecture, Blog, Event
from forms import RegistrationForm, LoginForm, EnrollmentForm, CourseForm, LectureForm
from utils import save_receipt, get_currency_from_country, calculate_enrollment_dates, format_currency
from captcha_utils import generate_math_captcha, verify_math_captcha
import os
import io
import uuid

# Blueprints
auth_bp      = Blueprint('auth',      __name__, url_prefix='/auth')
course_bp    = Blueprint('courses',   __name__, url_prefix='/courses')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
main_bp      = Blueprint('main',      __name__)


# ================================
# AUTHENTICATION ROUTES
# ================================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if request.method == 'GET':
        captcha_question = generate_math_captcha()

    if form.validate_on_submit():
        if not verify_math_captcha(form.captcha_answer.data):
            flash('Incorrect answer to security question. Please try again.', 'danger')
            captcha_question = generate_math_captcha()
            return render_template('auth/register.html', form=form, captcha_question=captcha_question)

        user = User(
            email=form.email.data.lower().strip(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            designation=form.designation.data,
            city=form.city.data.strip(),
            country=form.country.data,
            education=form.education.data,
            university=form.university.data.strip(),
            is_active=False
        )
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f'New user registered (pending approval): {user.email}')
            flash('Registration successful! Your account is pending admin approval.', 'info')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {str(e)}')
            flash('An error occurred during registration. Please try again.', 'danger')

    if request.method == 'GET' or not form.validate_on_submit():
        captcha_question = generate_math_captcha()

    return render_template('auth/register.html', form=form, captcha_question=captcha_question)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Your account is pending admin approval.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        current_app.logger.info(f'User logged in: {user.email}')

        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        return redirect(next_page)

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    current_app.logger.info(f'User logged out: {current_user.email}')
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


# ================================
# MAIN / PUBLIC ROUTES
# ================================

@main_bp.route('/')
def index():
    courses = Course.query.filter_by(is_active=True).all()
    recent_blogs = Blog.query.filter_by(is_published=True).order_by(Blog.created_at.desc()).limit(3).all()
    upcoming_events = Event.query.filter(
        Event.is_active == True,
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date).limit(3).all()

    return render_template('public/home.html',
                           featured_courses=courses,
                           courses=courses,
                           blogs=recent_blogs,
                           events=upcoming_events)


@main_bp.route('/courses')
def courses():
    courses = Course.query.filter_by(is_active=True).all()
    return render_template('public/courses.html', courses=courses)


@main_bp.route('/about')
def about():
    return render_template('public/about.html')


@main_bp.route('/contact')
def contact():
    return render_template('public/contact.html')


# ================================
# COURSE ROUTES
# ================================

@course_bp.route('/<slug>')
def detail(slug):
    course = Course.query.filter_by(slug=slug, is_active=True).first_or_404()
    lectures = course.lectures.order_by(Lecture.order_number).all()

    is_enrolled       = False
    active_enrollment = None

    if current_user.is_authenticated:
        active_enrollment = Enrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course.id,
            status='approved'
        ).first()
        if active_enrollment and active_enrollment.is_active():
            is_enrolled = True

    duration_tiers = current_app.config.get('DURATION_TIERS', {})

    from models import CourseMaterial, CourseTest

    materials = CourseMaterial.query.filter_by(
        course_id=course.id, is_active=True
    ).order_by(CourseMaterial.order_number).all()

    tests = CourseTest.query.filter_by(
        course_id=course.id, is_active=True
    ).order_by(CourseTest.order_number).all()

    return render_template('courses/course_detail.html',
                        course=course,
                        lectures=lectures,
                        is_enrolled=is_enrolled,
                        enrollment=active_enrollment,
                        duration_tiers=duration_tiers,
                        materials=materials,
                        tests=tests)


@course_bp.route('/<slug>/enroll', methods=['GET', 'POST'])
@login_required
def enroll(slug):
    """Course enrollment with duration-tier + learning mode pricing."""
    course = Course.query.filter_by(slug=slug, is_active=True).first_or_404()
    duration_tiers = current_app.config.get('DURATION_TIERS', {})

    # Block if already pending or approved
    existing = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course.id
    ).filter(Enrollment.status.in_(['pending', 'approved'])).first()

    if existing:
        if existing.status == 'pending':
            flash('You already have a pending enrollment for this course.', 'warning')
        else:
            flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('courses.detail', slug=slug))

    form = EnrollmentForm()

    if request.method == 'POST':
        try:
            # ── Duration tier ─────────────────────────────────
            tier_key = request.form.get('duration_tier', 'short')
            tier     = duration_tiers.get(tier_key)

            if not tier:
                flash('Invalid duration tier selected.', 'danger')
                return render_template('courses/enroll.html',
                                       form=form, course=course,
                                       duration_tiers=duration_tiers,
                                       user=current_user)

            # ── Learning mode ──────────────────────────────────
            learning_mode  = request.form.get('learning_mode', '').strip()
            preferred_city = request.form.get('preferred_city', '').strip()
            preferred_days = request.form.get('preferred_days', '').strip()
            preferred_time = request.form.get('preferred_time', '').strip()
            schedule_notes = request.form.get('schedule_notes', '').strip()

            if not learning_mode:
                flash('Please select a learning mode.', 'danger')
                return render_template('courses/enroll.html',
                                       form=form, course=course,
                                       duration_tiers=duration_tiers,
                                       user=current_user)

            is_face_to_face = learning_mode.startswith('face_to_face')

            # Face-to-face requires schedule fields
            if is_face_to_face and (not preferred_days or not preferred_time):
                flash('Please fill in your preferred days and time for face-to-face classes.', 'danger')
                return render_template('courses/enroll.html',
                                       form=form, course=course,
                                       duration_tiers=duration_tiers,
                                       user=current_user)

            # ── Price calculation ──────────────────────────────
            course_level     = course.level.lower()
            is_international = current_user.country != 'Pakistan'

            level_prices = tier.get(course_level, tier.get('beginner', {}))
            base_price_pkr = level_prices.get('pkr', 0)

            # Apply 3× for face-to-face
            price_pkr = base_price_pkr * 3 if is_face_to_face else base_price_pkr

            # Apply 2× for international
            if is_international:
                price_pkr = price_pkr * 2

            price_pkr  = round(price_pkr)
            total_days = tier['total_days']

            # ── Payment method ─────────────────────────────────
            payment_method = request.form.get('payment_method', '').strip()
            if not payment_method:
                flash('Please select a payment method.', 'danger')
                return render_template('courses/enroll.html',
                                       form=form, course=course,
                                       duration_tiers=duration_tiers,
                                       user=current_user)

            # ── Receipt upload ─────────────────────────────────
            receipt_file = request.files.get('payment_receipt')
            if not receipt_file or receipt_file.filename == '':
                flash('Please upload a payment receipt.', 'danger')
                return render_template('courses/enroll.html',
                                       form=form, course=course,
                                       duration_tiers=duration_tiers,
                                       user=current_user)

            receipt_filename = save_receipt(receipt_file)
            if not receipt_filename:
                flash('Failed to upload receipt. Please try again.', 'danger')
                return render_template('courses/enroll.html',
                                       form=form, course=course,
                                       duration_tiers=duration_tiers,
                                       user=current_user)

            # ── Create enrollment ──────────────────────────────
            enrollment = Enrollment(
                user_id=current_user.id,
                course_id=course.id,
                enrollment_type=tier_key,
                duration_value=tier['months'],
                total_days=total_days,
                price_paid_pkr=price_pkr,
                currency='USD' if is_international else 'PKR',
                payment_method=payment_method,
                payment_receipt=receipt_filename,
                status='pending',
                # New learning mode fields
                learning_mode=learning_mode,
                preferred_city=preferred_city if is_face_to_face else None,
                preferred_days=preferred_days if is_face_to_face else None,
                preferred_time=preferred_time if is_face_to_face else None,
                schedule_notes=schedule_notes if is_face_to_face else None,
            )

            db.session.add(enrollment)
            db.session.commit()

            mode_label = {
                'self_paced':              'Self-Paced (Recorded)',
                'live_online':             'Live Online',
                'face_to_face_lahore':     'Face to Face — Lahore',
                'face_to_face_faisalabad': 'Face to Face — Faisalabad',
            }.get(learning_mode, learning_mode)

            current_app.logger.info(
                f'Enrollment: User={current_user.id}, Course={course.id}, '
                f'Tier={tier_key}, Mode={learning_mode}, Days={total_days}, Price=Rs.{price_pkr}'
            )

            flash(
                f'Enrollment submitted! {tier["label"]} plan · {mode_label} · '
                f'Rs. {price_pkr:,}. Awaiting admin approval.',
                'success'
            )
            return redirect(url_for('dashboard.my_enrollments'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Enrollment error: {str(e)}')
            flash('An error occurred. Please try again.', 'danger')

    return render_template('courses/enroll.html',
                           form=form,
                           course=course,
                           duration_tiers=duration_tiers,
                           user=current_user)


@course_bp.route('/<slug>/lecture/<int:lecture_id>')
@login_required
def lecture(slug, lecture_id):
    course  = Course.query.filter_by(slug=slug, is_active=True).first_or_404()
    lecture = Lecture.query.get_or_404(lecture_id)

    if lecture.course_id != course.id:
        flash('Invalid lecture', 'danger')
        return redirect(url_for('courses.detail', slug=slug))

    has_access = False
    if lecture.is_free:
        has_access = True
    else:
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course.id,
            status='approved'
        ).first()
        if enrollment and enrollment.is_active():
            has_access = True

    if not has_access:
        flash('You need to enroll in this course to access this lecture.', 'warning')
        return redirect(url_for('courses.detail', slug=slug))

    all_lectures = course.lectures.order_by(Lecture.order_number).all()
    return render_template('courses/lecture.html',
                           course=course,
                           lecture=lecture,
                           all_lectures=all_lectures)


# ================================
# DASHBOARD ROUTES
# ================================

@dashboard_bp.route('/')
@login_required
def index():
    active_enrollments = Enrollment.query.filter_by(
        user_id=current_user.id,
        status='approved'
    ).all()
    active_enrollments = [e for e in active_enrollments if e.is_active()]

    pending_enrollments = Enrollment.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).all()

    return render_template('dashboard/dashboard.html',
                           active_enrollments=active_enrollments,
                           pending_enrollments=pending_enrollments)


@dashboard_bp.route('/enrollments')
@login_required
def my_enrollments():
    enrollments = Enrollment.query.filter_by(
        user_id=current_user.id
    ).order_by(Enrollment.enrolled_at.desc()).all()
    return render_template('dashboard/enrollments.html', enrollments=enrollments)


@dashboard_bp.route('/profile')
@login_required
def profile():
    return render_template('dashboard/profile.html', user=current_user)


# ================================
# CERTIFICATE DOWNLOAD
# ================================

@dashboard_bp.route('/certificate/<int:enrollment_id>/download')
@login_required
def download_certificate(enrollment_id):
    from certificate_utils import generate_certificate

    enrollment = Enrollment.query.get_or_404(enrollment_id)

    if enrollment.user_id != current_user.id:
        flash('You do not have permission to download this certificate.', 'danger')
        return redirect(url_for('dashboard.index'))

    if not enrollment.is_completed or not enrollment.completed_at:
        flash('Certificate is only available after course completion.', 'warning')
        return redirect(url_for('dashboard.index'))

    if not enrollment.certificate_id:
        enrollment.certificate_id = str(uuid.uuid4()).replace('-', '').upper()[:16]
        db.session.commit()

    student_name = f"{enrollment.student.first_name} {enrollment.student.last_name}"
    pdf_bytes = generate_certificate(
        student_name=student_name,
        course_name=enrollment.course.title,
        completed_at=enrollment.completed_at,
        cert_id=enrollment.certificate_id,
    )

    filename = f"EduLearn_Certificate_{enrollment.course.slug}_{enrollment.certificate_id}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename,
    )


# ================================
# UPLOADS / STATIC FILE SERVING
# ================================

@main_bp.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(os.path.join(upload_folder, folder), filename)


# Add this route to routes.py alongside the existing uploaded_file route
# It serves materials and test files uploaded by admin

@main_bp.route('/uploads/materials/<filename>')
def material_file(filename):
    """Serve course material files."""
    import os
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'materials')
    return send_from_directory(folder, filename)

@main_bp.route('/uploads/tests/<filename>')
def test_file(filename):
    """Serve course test files."""
    import os
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'tests')
    return send_from_directory(folder, filename)