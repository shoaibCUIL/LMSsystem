from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from datetime import datetime, timedelta
from database import db
from models import User, Course, Enrollment, Lecture, Blog, Event
from forms import RegistrationForm, LoginForm, EnrollmentForm, CourseForm, LectureForm
from utils import save_receipt, get_currency_from_country, calculate_enrollment_dates, format_currency, calculate_multi_course_discount
from captcha_utils import generate_math_captcha, verify_math_captcha
import os

# Blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
course_bp = Blueprint('courses', __name__, url_prefix='/courses')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
main_bp = Blueprint('main', __name__)


# ================================
# AUTHENTICATION ROUTES
# ================================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Enhanced registration with custom CAPTCHA"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    # Generate CAPTCHA question for GET request
    if request.method == 'GET':
        captcha_question = generate_math_captcha()
    
    if form.validate_on_submit():
        # Verify custom CAPTCHA
        if not verify_math_captcha(form.captcha_answer.data):
            flash('Incorrect answer to security question. Please try again.', 'danger')
            # Generate new CAPTCHA for retry
            captcha_question = generate_math_captcha()
            return render_template('auth/register.html', form=form, captcha_question=captcha_question)
        
        # Create user
        user = User(
            email=form.email.data.lower().strip(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            designation=form.designation.data,
            city=form.city.data.strip(),
            country=form.country.data,
            education=form.education.data,
            university=form.university.data.strip()
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            current_app.logger.info(f'New user registered: {user.email} from {user.country}')
            flash('Registration successful! Please login to continue.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {str(e)}')
            flash('An error occurred during registration. Please try again.', 'danger')
    
    # Generate CAPTCHA for display (GET or failed POST)
    if request.method == 'GET' or not form.validate_on_submit():
        captcha_question = generate_math_captcha()
    
    return render_template('auth/register.html', form=form, captcha_question=captcha_question)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        current_app.logger.info(f'User logged in: {user.email}')
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    current_app.logger.info(f'User logged out: {current_user.email}')
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


# ================================
# MAIN/PUBLIC ROUTES
# ================================

@main_bp.route('/')
def index():
    """Homepage"""
    courses = Course.query.filter_by(is_active=True).all()
    recent_blogs = Blog.query.filter_by(is_published=True).order_by(Blog.created_at.desc()).limit(3).all()
    upcoming_events = Event.query.filter(
        Event.is_active == True,
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date).limit(3).all()
    
    return render_template('public/home.html', 
                          courses=courses,
                          blogs=recent_blogs,
                          events=upcoming_events)


@main_bp.route('/courses')
def courses():
    """List all courses"""
    courses = Course.query.filter_by(is_active=True).all()
    return render_template('public/courses.html', courses=courses)


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('public/about.html')


@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('public/contact.html')


# ================================
# COURSE ROUTES
# ================================

@course_bp.route('/<slug>')
def detail(slug):
    """Course detail page"""
    course = Course.query.filter_by(slug=slug, is_active=True).first_or_404()
    lectures = course.lectures.order_by(Lecture.order_number).all()
    
    # Check if user is enrolled
    is_enrolled = False
    active_enrollment = None
    
    if current_user.is_authenticated:
        active_enrollment = Enrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course.id,
            status='approved'
        ).first()
        
        if active_enrollment and active_enrollment.is_active():
            is_enrolled = True
    
    return render_template('courses/course_detail.html',
                          course=course,
                          lectures=lectures,
                          is_enrolled=is_enrolled,
                          enrollment=active_enrollment)


@course_bp.route('/<slug>/enroll', methods=['GET', 'POST'])
@login_required
def enroll(slug):
    """Course enrollment with payment"""
    course = Course.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course.id
    ).filter(Enrollment.status.in_(['pending', 'approved'])).first()
    
    if existing_enrollment:
        if existing_enrollment.status == 'pending':
            flash('You already have a pending enrollment request for this course.', 'warning')
        else:
            flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('courses.detail', slug=slug))
    
    form = EnrollmentForm()
    
    if form.validate_on_submit():
        try:
            # Calculate total days and price
            enrollment_type = form.enrollment_type.data
            total_days = 0
            price_pkr = 0
            
            if enrollment_type == 'custom_price':
                price_pkr = form.custom_price.data
                total_days = course.calculate_days(price_pkr)
            else:
                duration_value = form.duration_value.data
                
                if enrollment_type == 'days':
                    total_days = duration_value
                elif enrollment_type == 'weeks':
                    total_days = duration_value * 7
                elif enrollment_type == 'months':
                    total_days = duration_value * 30
                
                total_days = max(total_days, course.min_days)
                price_pkr = course.calculate_price(days=total_days)
            
            # Apply international pricing if needed
            if current_user.country != 'Pakistan':
                price_pkr *= current_app.config['INTERNATIONAL_MULTIPLIER']
            
            # Ensure minimum price
            price_pkr = max(price_pkr, course.min_price_pkr)
            
            # Apply multi-course discount (10% off for 2+ courses)
            final_price, discount, has_discount = calculate_multi_course_discount(
                current_user.id, 
                price_pkr
            )
            
            # Save payment receipt
            receipt_file = form.payment_receipt.data
            receipt_filename = save_receipt(receipt_file)
            
            if not receipt_filename:
                flash('Failed to upload payment receipt. Please try again.', 'danger')
                return render_template('courses/enroll.html', form=form, course=course, user=current_user)
            
            # Create enrollment
            enrollment = Enrollment(
                user_id=current_user.id,
                course_id=course.id,
                enrollment_type=enrollment_type,
                duration_value=form.duration_value.data or 0,
                total_days=total_days,
                price_paid_pkr=final_price,  # Use discounted price
                currency=get_currency_from_country(current_user.country),
                payment_method=form.payment_method.data,
                payment_receipt=receipt_filename,
                status='pending'
            )
            
            db.session.add(enrollment)
            db.session.commit()
            
            current_app.logger.info(f'Enrollment request created: User={current_user.id}, Course={course.id}, Price={final_price}, Discount={discount if has_discount else 0}')
            
            flash_msg = 'Enrollment request submitted successfully! '
            if has_discount:
                flash_msg += f'You saved Rs. {discount:.0f} with our multi-course discount (10% off)! '
            flash_msg += 'You will receive confirmation once admin approves your payment.'
            flash(flash_msg, 'success')
            return redirect(url_for('dashboard.my_enrollments'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Enrollment error: {str(e)}')
            flash('An error occurred while processing your enrollment. Please try again.', 'danger')
    
    return render_template('courses/enroll.html', form=form, course=course, user=current_user)


@course_bp.route('/<slug>/lecture/<int:lecture_id>')
@login_required
def lecture(slug, lecture_id):
    """View individual lecture"""
    course = Course.query.filter_by(slug=slug, is_active=True).first_or_404()
    lecture = Lecture.query.get_or_404(lecture_id)
    
    # Verify lecture belongs to course
    if lecture.course_id != course.id:
        flash('Invalid lecture', 'danger')
        return redirect(url_for('courses.detail', slug=slug))
    
    # Check access permission
    has_access = False
    
    if lecture.is_free:
        has_access = True
    else:
        # Check if user has active enrollment
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
    
    # Get all lectures for navigation
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
    """User dashboard"""
    # Get active enrollments
    active_enrollments = Enrollment.query.filter_by(
        user_id=current_user.id,
        status='approved'
    ).all()
    
    # Filter truly active enrollments
    active_enrollments = [e for e in active_enrollments if e.is_active()]
    
    # Get pending enrollments
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
    """View all enrollments"""
    enrollments = Enrollment.query.filter_by(
        user_id=current_user.id
    ).order_by(Enrollment.enrolled_at.desc()).all()
    
    return render_template('dashboard/enrollments.html', enrollments=enrollments)


@dashboard_bp.route('/profile')
@login_required
def profile():
    """User profile"""
    return render_template('dashboard/profile.html', user=current_user)


# ================================
# UPLOADS/STATIC FILE SERVING
# ================================

@main_bp.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    """Serve uploaded files (receipts, thumbnails)"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(os.path.join(upload_folder, folder), filename)