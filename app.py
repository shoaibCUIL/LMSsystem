"""
Main Application File for LMS System
Complete Flask application with all routes and logic
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os
import re

from models import db, User, Course, Lecture, Enrollment, Blog, Event, CustomBundle, Tag
from config import get_config


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Ensure instance folder exists
os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


def create_slug(text):
    """Create URL-friendly slug from text"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return render_template('errors/403.html'), 403


# ==================== CONTEXT PROCESSORS ====================

@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    return {
        'app_name': app.config['APP_NAME'],
        'current_year': datetime.utcnow().year,
        'categories': app.config['COURSE_CATEGORIES']
    }


# ==================== PUBLIC ROUTES ====================

@app.route('/')
def home():
    """Homepage with featured courses"""
    featured_courses = Course.query.filter_by(
        is_published=True, 
        featured=True
    ).limit(6).all()
    
    recent_courses = Course.query.filter_by(
        is_published=True
    ).order_by(Course.created_at.desc()).limit(8).all()
    
    recent_blogs = Blog.query.filter_by(
        is_published=True
    ).order_by(Blog.published_at.desc()).limit(3).all()
    
    stats = {
        'total_courses': Course.query.filter_by(is_published=True).count(),
        'total_students': User.query.filter_by(is_admin=False).count(),
        'total_enrollments': Enrollment.query.filter_by(is_active=True).count()
    }
    
    return render_template('public/home.html', 
                         featured_courses=featured_courses,
                         recent_courses=recent_courses,
                         recent_blogs=recent_blogs,
                         stats=stats)


@app.route('/courses')
def courses():
    """Course listing page with filters"""
    # Get filter parameters
    category = request.args.get('category', '')
    level = request.args.get('level', '')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    
    # Base query
    query = Course.query.filter_by(is_published=True)
    
    # Apply filters
    if category:
        query = query.filter_by(category=category)
    
    if level:
        query = query.filter_by(level=level)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Course.title.ilike(search_term),
                Course.description.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort == 'newest':
        query = query.order_by(Course.created_at.desc())
    elif sort == 'oldest':
        query = query.order_by(Course.created_at.asc())
    elif sort == 'price_low':
        query = query.order_by(Course.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Course.price.desc())
    elif sort == 'popular':
        # Sort by enrollment count (requires subquery or join)
        query = query.order_by(Course.id.desc())  # Placeholder
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = app.config['COURSES_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    courses_list = pagination.items
    
    return render_template('public/courses.html',
                         courses=courses_list,
                         pagination=pagination,
                         category=category,
                         level=level,
                         search=search,
                         sort=sort,
                         levels=app.config['COURSE_LEVELS'])


@app.route('/course/<int:course_id>')
def course_detail(course_id):
    """Individual course detail page"""
    course = Course.query.get_or_404(course_id)
    
    if not course.is_published and (not current_user.is_authenticated or not current_user.is_admin):
        abort(404)
    
    lectures = course.lectures.order_by(Lecture.order_index.asc()).all()
    
    is_enrolled = False
    enrollment = None
    
    if current_user.is_authenticated:
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course_id,
            is_active=True
        ).first()
        is_enrolled = enrollment is not None
    
    return render_template('public/course_detail.html',
                         course=course,
                         lectures=lectures,
                         is_enrolled=is_enrolled,
                         enrollment=enrollment)


@app.route('/blogs')
def blogs():
    """Blog listing page"""
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Blog.query.filter_by(is_published=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Blog.title.ilike(search_term),
                Blog.content.ilike(search_term),
                Blog.excerpt.ilike(search_term)
            )
        )
    
    query = query.order_by(Blog.published_at.desc())
    
    page = request.args.get('page', 1, type=int)
    per_page = app.config['BLOGS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    blogs_list = pagination.items
    
    return render_template('public/blogs.html',
                         blogs=blogs_list,
                         pagination=pagination,
                         category=category,
                         search=search,
                         blog_categories=app.config['BLOG_CATEGORIES'])


@app.route('/blog/<slug>')
def blog_detail(slug):
    """Individual blog detail page"""
    blog = Blog.query.filter_by(slug=slug).first_or_404()
    
    if not blog.is_published and (not current_user.is_authenticated or not current_user.is_admin):
        abort(404)
    
    # Increment view count
    blog.increment_views()
    
    # Get related blogs
    related_blogs = Blog.query.filter(
        Blog.id != blog.id,
        Blog.category == blog.category,
        Blog.is_published == True
    ).limit(3).all()
    
    return render_template('public/blog_detail.html',
                         blog=blog,
                         related_blogs=related_blogs)


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        
        if not email or '@' not in email:
            errors.append('Valid email address is required.')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            new_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            app.logger.error(f'Registration error: {str(e)}')
    
    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Please provide both username and password.', 'danger')
            return render_template('auth/login.html')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return render_template('auth/login.html')
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log in user
            login_user(user, remember=remember)
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password.', 'danger')
    
    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))


# ==================== USER DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing enrolled courses"""
    # Get active enrollments
    enrollments = Enrollment.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).order_by(Enrollment.enrolled_at.desc()).all()
    
    # Get custom bundles
    bundles = CustomBundle.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).order_by(CustomBundle.created_at.desc()).all()
    
    # Calculate stats
    stats = {
        'total_courses': len(enrollments),
        'total_bundles': len(bundles),
        'completed_courses': len([e for e in enrollments if e.completed_at]),
        'in_progress': len([e for e in enrollments if not e.completed_at])
    }
    
    return render_template('dashboard/dashboard.html',
                         enrollments=enrollments,
                         bundles=bundles,
                         stats=stats)


@app.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll user in a course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        if existing_enrollment.is_active:
            flash('You are already enrolled in this course.', 'info')
            return redirect(url_for('course_detail', course_id=course_id))
        else:
            # Reactivate enrollment
            existing_enrollment.is_active = True
            existing_enrollment.enrolled_at = datetime.utcnow()
            flash('Your enrollment has been reactivated!', 'success')
    else:
        # Create new enrollment
        try:
            enrollment = Enrollment(
                user_id=current_user.id,
                course_id=course_id,
                enrolled_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=app.config['DEFAULT_COURSE_DURATION'])
            )
            db.session.add(enrollment)
            flash(f'Successfully enrolled in {course.title}!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during enrollment. Please try again.', 'danger')
            app.logger.error(f'Enrollment error: {str(e)}')
            return redirect(url_for('course_detail', course_id=course_id))
    
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/unenroll/<int:enrollment_id>', methods=['POST'])
@login_required
def unenroll_course(enrollment_id):
    """Unenroll from a course"""
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    # Verify ownership
    if enrollment.user_id != current_user.id:
        abort(403)
    
    enrollment.is_active = False
    db.session.commit()
    
    flash('You have been unenrolled from the course.', 'info')
    return redirect(url_for('dashboard'))


# ==================== CUSTOM BUNDLE ROUTES ====================

@app.route('/bundle/creator')
@login_required
def bundle_creator():
    """Custom bundle creation page"""
    all_courses = Course.query.filter_by(is_published=True).all()
    return render_template('dashboard/bundle_creator.html', courses=all_courses)


@app.route('/bundle/create', methods=['POST'])
@login_required
def create_bundle():
    """Create custom course bundle"""
    bundle_name = request.form.get('bundle_name', '').strip()
    description = request.form.get('description', '').strip()
    duration_days = request.form.get('duration_days', type=int)
    course_ids = request.form.getlist('course_ids')
    
    # Validation
    if not bundle_name:
        flash('Bundle name is required.', 'danger')
        return redirect(url_for('bundle_creator'))
    
    if not course_ids or len(course_ids) < 2:
        flash('Please select at least 2 courses for the bundle.', 'danger')
        return redirect(url_for('bundle_creator'))
    
    if len(course_ids) > app.config['MAX_BUNDLE_COURSES']:
        flash(f'Maximum {app.config["MAX_BUNDLE_COURSES"]} courses allowed per bundle.', 'danger')
        return redirect(url_for('bundle_creator'))
    
    if not duration_days or duration_days < 1:
        duration_days = 30
    
    try:
        # Create bundle
        bundle = CustomBundle(
            user_id=current_user.id,
            bundle_name=bundle_name,
            description=description,
            course_ids=','.join(course_ids),
            duration_days=duration_days,
            discount_percentage=app.config['BUNDLE_DISCOUNT_PERCENTAGE']
        )
        
        # Calculate pricing
        bundle.calculate_pricing()
        
        db.session.add(bundle)
        db.session.commit()
        
        flash(f'Bundle "{bundle_name}" created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while creating the bundle.', 'danger')
        app.logger.error(f'Bundle creation error: {str(e)}')
        return redirect(url_for('bundle_creator'))


@app.route('/bundle/<int:bundle_id>/activate', methods=['POST'])
@login_required
def activate_bundle(bundle_id):
    """Activate a custom bundle"""
    bundle = CustomBundle.query.get_or_404(bundle_id)
    
    # Verify ownership
    if bundle.user_id != current_user.id:
        abort(403)
    
    if bundle.is_expired:
        flash('This bundle has expired.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Activate bundle
    bundle.activate_bundle()
    
    # Enroll in all courses
    courses = bundle.get_courses()
    enrolled_count = 0
    
    for course in courses:
        # Check if already enrolled
        existing = Enrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course.id
        ).first()
        
        if not existing:
            enrollment = Enrollment(
                user_id=current_user.id,
                course_id=course.id,
                enrolled_at=datetime.utcnow(),
                expires_at=bundle.expires_at
            )
            db.session.add(enrollment)
            enrolled_count += 1
        elif not existing.is_active:
            existing.is_active = True
            existing.enrolled_at = datetime.utcnow()
            existing.expires_at = bundle.expires_at
            enrolled_count += 1
    
    db.session.commit()
    
    flash(f'Bundle activated! Enrolled in {enrolled_count} courses.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/bundle/<int:bundle_id>/delete', methods=['POST'])
@login_required
def delete_bundle(bundle_id):
    """Delete a custom bundle"""
    bundle = CustomBundle.query.get_or_404(bundle_id)
    
    # Verify ownership
    if bundle.user_id != current_user.id:
        abort(403)
    
    db.session.delete(bundle)
    db.session.commit()
    
    flash('Bundle deleted successfully.', 'info')
    return redirect(url_for('dashboard'))


# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    """Admin dashboard"""
    stats = {
        'total_users': User.query.count(),
        'total_courses': Course.query.count(),
        'total_enrollments': Enrollment.query.filter_by(is_active=True).count(),
        'total_blogs': Blog.query.count(),
        'total_lectures': Lecture.query.count(),
        'active_bundles': CustomBundle.query.filter_by(is_active=True).count()
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_enrollments = Enrollment.query.order_by(Enrollment.enrolled_at.desc()).limit(10).all()
    
    courses = Course.query.order_by(Course.created_at.desc()).all()
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    
    return render_template('admin/admin.html',
                         stats=stats,
                         recent_users=recent_users,
                         recent_enrollments=recent_enrollments,
                         courses=courses,
                         blogs=blogs,
                         categories=app.config['COURSE_CATEGORIES'],
                         levels=app.config['COURSE_LEVELS'],
                         blog_categories=app.config['BLOG_CATEGORIES'])


@app.route('/admin/course/add', methods=['POST'])
@login_required
@admin_required
def admin_add_course():
    """Add new course"""
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()
    level = request.form.get('level', 'Beginner')
    price = request.form.get('price', type=float, default=0.0)
    duration_hours = request.form.get('duration_hours', type=int, default=0)
    instructor_name = request.form.get('instructor_name', '').strip()
    thumbnail_url = request.form.get('thumbnail_url', '').strip()
    featured = request.form.get('featured') == 'on'
    
    # Validation
    if not title or not description or not category:
        flash('Title, description, and category are required.', 'danger')
        return redirect(url_for('admin_panel'))
    
    try:
        course = Course(
            title=title,
            description=description,
            category=category,
            level=level,
            price=price,
            duration_hours=duration_hours,
            instructor_name=instructor_name,
            thumbnail_url=thumbnail_url,
            featured=featured,
            is_published=True
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash(f'Course "{title}" added successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while adding the course.', 'danger')
        app.logger.error(f'Add course error: {str(e)}')
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/course/<int:course_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_course(course_id):
    """Edit existing course"""
    course = Course.query.get_or_404(course_id)
    
    course.title = request.form.get('title', '').strip()
    course.description = request.form.get('description', '').strip()
    course.category = request.form.get('category', '').strip()
    course.level = request.form.get('level', 'Beginner')
    course.price = request.form.get('price', type=float, default=0.0)
    course.duration_hours = request.form.get('duration_hours', type=int, default=0)
    course.instructor_name = request.form.get('instructor_name', '').strip()
    course.thumbnail_url = request.form.get('thumbnail_url', '').strip()
    course.featured = request.form.get('featured') == 'on'
    course.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        flash(f'Course "{course.title}" updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the course.', 'danger')
        app.logger.error(f'Edit course error: {str(e)}')
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/course/<int:course_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_course(course_id):
    """Delete course"""
    course = Course.query.get_or_404(course_id)
    
    try:
        db.session.delete(course)
        db.session.commit()
        flash(f'Course "{course.title}" deleted successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the course.', 'danger')
        app.logger.error(f'Delete course error: {str(e)}')
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/lecture/add', methods=['POST'])
@login_required
@admin_required
def admin_add_lecture():
    """Add lecture to course"""
    course_id = request.form.get('course_id', type=int)
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    video_url = request.form.get('video_url', '').strip()
    duration_minutes = request.form.get('duration_minutes', type=int, default=0)
    order_index = request.form.get('order_index', type=int, default=0)
    is_preview = request.form.get('is_preview') == 'on'
    
    if not course_id or not title or not video_url:
        flash('Course, title, and video URL are required.', 'danger')
        return redirect(url_for('admin_panel'))
    
    course = Course.query.get_or_404(course_id)
    
    try:
        lecture = Lecture(
            course_id=course_id,
            title=title,
            description=description,
            video_url=video_url,
            duration_minutes=duration_minutes,
            order_index=order_index,
            is_preview=is_preview
        )
        
        db.session.add(lecture)
        db.session.commit()
        
        flash(f'Lecture "{title}" added to "{course.title}"!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while adding the lecture.', 'danger')
        app.logger.error(f'Add lecture error: {str(e)}')
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/lecture/<int:lecture_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_lecture(lecture_id):
    """Delete lecture"""
    lecture = Lecture.query.get_or_404(lecture_id)
    
    try:
        db.session.delete(lecture)
        db.session.commit()
        flash(f'Lecture "{lecture.title}" deleted successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the lecture.', 'danger')
        app.logger.error(f'Delete lecture error: {str(e)}')
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/blog/add', methods=['POST'])
@login_required
@admin_required
def admin_add_blog():
    """Add new blog post"""
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    excerpt = request.form.get('excerpt', '').strip()
    author = request.form.get('author', '').strip() or current_user.full_name
    category = request.form.get('category', '').strip()
    tags = request.form.get('tags', '').strip()
    featured_image = request.form.get('featured_image', '').strip()
    
    if not title or not content:
        flash('Title and content are required.', 'danger')
        return redirect(url_for('admin_panel'))
    
    # Create slug
    slug = create_slug(title)
    
    # Ensure slug is unique
    base_slug = slug
    counter = 1
    while Blog.query.filter_by(slug=slug).first():
        slug = f'{base_slug}-{counter}'
        counter += 1
    
    try:
        blog = Blog(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt or content[:200],
            author=author,
            category=category,
            tags=tags,
            featured_image=featured_image,
            is_published=True,
            published_at=datetime.utcnow()
        )
        
        db.session.add(blog)
        db.session.commit()
        
        flash(f'Blog post "{title}" published successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while publishing the blog post.', 'danger')
        app.logger.error(f'Add blog error: {str(e)}')
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/blog/<int:blog_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_blog(blog_id):
    """Delete blog post"""
    blog = Blog.query.get_or_404(blog_id)
    
    try:
        db.session.delete(blog)
        db.session.commit()
        flash(f'Blog post "{blog.title}" deleted successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the blog post.', 'danger')
        app.logger.error(f'Delete blog error: {str(e)}')
    
    return redirect(url_for('admin_panel'))


# ==================== API ENDPOINTS (for future frontend) ====================

@app.route('/api/courses')
def api_courses():
    """API endpoint for courses"""
    courses = Course.query.filter_by(is_published=True).all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'category': c.category,
        'price': c.price,
        'level': c.level
    } for c in courses])


@app.route('/api/course/<int:course_id>')
def api_course_detail(course_id):
    """API endpoint for course detail"""
    course = Course.query.get_or_404(course_id)
    lectures = course.lectures.order_by(Lecture.order_index.asc()).all()
    
    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'category': course.category,
        'price': course.price,
        'level': course.level,
        'lectures': [{
            'id': l.id,
            'title': l.title,
            'duration': l.duration_minutes
        } for l in lectures]
    })


# ==================== DATABASE INITIALIZATION ====================

@app.cli.command('init-db')
def init_db():
    """Initialize database with tables"""
    db.create_all()
    print('Database initialized successfully!')


@app.cli.command('create-admin')
def create_admin():
    """Create admin user"""
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print('Admin user already exists!')
        return
    
    admin = User(
        username='admin',
        email='admin@learnhub.com',
        first_name='Admin',
        last_name='User',
        is_admin=True
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    
    print('Admin user created successfully!')
    print('Username: admin')
    print('Password: admin123')


@app.cli.command('seed-data')
def seed_data():
    """Seed database with sample data"""
    # Create sample courses
    courses_data = [
        {
            'title': 'Complete Python Programming',
            'description': 'Learn Python from scratch to advanced level with hands-on projects.',
            'category': 'Programming',
            'level': 'Beginner',
            'price': 49.99,
            'duration_hours': 40,
            'instructor_name': 'John Doe',
            'thumbnail_url': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=500',
            'featured': True
        },
        {
            'title': 'Web Development Bootcamp',
            'description': 'Master HTML, CSS, JavaScript, and modern frameworks.',
            'category': 'Web Development',
            'level': 'Intermediate',
            'price': 59.99,
            'duration_hours': 60,
            'instructor_name': 'Jane Smith',
            'thumbnail_url': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=500',
            'featured': True
        },
        {
            'title': 'Data Science with Python',
            'description': 'Learn data analysis, visualization, and machine learning.',
            'category': 'Data Science',
            'level': 'Advanced',
            'price': 79.99,
            'duration_hours': 50,
            'instructor_name': 'Dr. Michael Chen',
            'thumbnail_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500',
            'featured': True
        }
    ]
    
    for course_data in courses_data:
        if not Course.query.filter_by(title=course_data['title']).first():
            course = Course(**course_data)
            db.session.add(course)
    
    db.session.commit()
    print('Sample data seeded successfully!')


# Add this route after the enroll_course route (around line 450)

@app.route('/payment/<int:course_id>')
@login_required
def payment_instructions(course_id):
    """Payment instructions page"""
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id,
        is_active=True
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('public/payment_instructions.html', course=course)


# Add these routes after admin_delete_blog (around line 750)

@app.route('/admin/blogs')
@login_required
@admin_required
def admin_blogs():
    """Admin blog management page"""
    filter_type = request.args.get('filter', 'all')
    
    query = Blog.query
    
    if filter_type == 'published':
        query = query.filter_by(is_published=True)
    elif filter_type == 'drafts':
        query = query.filter_by(is_published=False)
    
    blogs = query.order_by(Blog.created_at.desc()).all()
    
    stats = {
        'total': Blog.query.count(),
        'published': Blog.query.filter_by(is_published=True).count(),
        'drafts': Blog.query.filter_by(is_published=False).count(),
        'total_views': db.session.query(db.func.sum(Blog.views_count)).scalar() or 0
    }
    
    return render_template('admin/admin_blogs.html', 
                         blogs=blogs, 
                         stats=stats)


@app.route('/admin/blog/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_blog():
    """Create new blog post"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        category = request.form.get('category', '').strip()
        tags = request.form.get('tags', '').strip()
        featured_image_url = request.form.get('featured_image_url', '').strip()
        is_published = request.form.get('is_published') == 'on'
        save_draft = request.form.get('save_draft')
        
        if not title or not content:
            flash('Title and content are required.', 'danger')
            return render_template('admin/admin_create_blog.html')
        
        # Create slug if not provided
        if not slug:
            slug = create_slug(title)
        
        # Ensure slug is unique
        base_slug = slug
        counter = 1
        while Blog.query.filter_by(slug=slug).first():
            slug = f'{base_slug}-{counter}'
            counter += 1
        
        try:
            blog = Blog(
                title=title,
                slug=slug,
                content=content,
                excerpt=excerpt or content[:200],
                category=category,
                tags=tags,
                featured_image_url=featured_image_url,
                author=current_user.full_name,
                is_published=is_published if not save_draft else False,
                published_at=datetime.utcnow() if (is_published and not save_draft) else None
            )
            
            db.session.add(blog)
            db.session.commit()
            
            if save_draft:
                flash(f'Blog post "{title}" saved as draft.', 'success')
            else:
                flash(f'Blog post "{title}" published successfully!', 'success')
            
            return redirect(url_for('admin_blogs'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while saving the blog post.', 'danger')
            app.logger.error(f'Create blog error: {str(e)}')
    
    return render_template('admin/admin_create_blog.html')


@app.route('/admin/blog/<int:blog_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_blog(blog_id):
    """Edit existing blog post"""
    blog = Blog.query.get_or_404(blog_id)
    
    if request.method == 'POST':
        blog.title = request.form.get('title', '').strip()
        blog.slug = request.form.get('slug', '').strip()
        blog.content = request.form.get('content', '').strip()
        blog.excerpt = request.form.get('excerpt', '').strip()
        blog.category = request.form.get('category', '').strip()
        blog.tags = request.form.get('tags', '').strip()
        blog.featured_image_url = request.form.get('featured_image_url', '').strip()
        blog.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash(f'Blog post "{blog.title}" updated successfully!', 'success')
            return redirect(url_for('admin_blogs'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the blog post.', 'danger')
            app.logger.error(f'Edit blog error: {str(e)}')
    
    return render_template('admin/admin_edit_blog.html', blog=blog)


@app.route('/admin/blog/<int:blog_id>/publish', methods=['POST'])
@login_required
@admin_required
def admin_publish_blog(blog_id):
    """Publish a draft blog post"""
    blog = Blog.query.get_or_404(blog_id)
    
    blog.is_published = True
    blog.published_at = datetime.utcnow()
    
    try:
        db.session.commit()
        flash(f'Blog post "{blog.title}" published successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while publishing the blog post.', 'danger')
        app.logger.error(f'Publish blog error: {str(e)}')
    
    return redirect(url_for('admin_blogs'))


@app.route('/admin/blog/<int:blog_id>/unpublish', methods=['POST'])
@login_required
@admin_required
def admin_unpublish_blog(blog_id):
    """Unpublish a blog post"""
    blog = Blog.query.get_or_404(blog_id)
    
    blog.is_published = False
    
    try:
        db.session.commit()
        flash(f'Blog post "{blog.title}" unpublished.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while unpublishing the blog post.', 'danger')
        app.logger.error(f'Unpublish blog error: {str(e)}')
    
    return redirect(url_for('admin_blogs'))


# Also add these placeholder routes for admin navigation (after admin_blogs)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """User management page (placeholder)"""
    flash('User management feature coming soon!', 'info')
    return redirect(url_for('admin_panel'))


@app.route('/admin/courses')
@login_required
@admin_required
def admin_courses():
    """Course management page (placeholder)"""
    flash('Course management feature coming soon!', 'info')
    return redirect(url_for('admin_panel'))


@app.route('/admin/enrollments')
@login_required
@admin_required
def admin_enrollments():
    """Enrollment management page (placeholder)"""
    flash('Enrollment management feature coming soon!', 'info')
    return redirect(url_for('admin_panel'))


@app.route('/admin/bundles')
@login_required
@admin_required
def admin_bundles():
    """Bundle management page (placeholder)"""
    flash('Bundle management feature coming soon!', 'info')
    return redirect(url_for('admin_panel'))


@app.route('/admin/lectures')
@login_required
@admin_required
def admin_lectures():
    """Lecture management page (placeholder)"""
    flash('Lecture management feature coming soon!', 'info')
    return redirect(url_for('admin_panel'))
# ==================== APPLICATION ENTRY POINT ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@learnhub.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: username=admin, password=admin123')
    
    app.run(debug=True, host='0.0.0.0', port=5000)