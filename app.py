from flask import Flask, render_template, request, redirect, flash, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from config import Config
from models import db, User, Course, Lecture, Enrollment, Blog

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


# ================= HOME =================
@app.route('/')
def home():
    courses = Course.query.all()
    return render_template('public/home.html', courses=courses)


# ================= COURSES (WITH FILTER) =================
@app.route('/courses')
def courses():

    selected_category = request.args.get('category')

    if selected_category:
        courses = Course.query.filter_by(category=selected_category).all()
    else:
        courses = Course.query.all()

    categories = db.session.query(Course.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template(
        'public/courses.html',
        courses=courses,
        categories=categories,
        selected_category=selected_category
    )


# ================= BLOG SYSTEM =================
@app.route('/blogs')
def blogs():
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('public/blogs.html', blogs=blogs)


@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('public/blog_detail.html', blog=blog)


# ================= AUTH =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        if request.form['password'] != request.form['confirm_password']:
            flash("Passwords do not match ❌")
            return redirect('/register')

        user = User(
            email=request.form['email'],
            password=generate_password_hash(request.form['password'])
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully ✅")
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect('/dashboard')
        else:
            flash("Invalid credentials ❌")

    return render_template('login.html')


# ================= DASHBOARD =================
@app.route('/dashboard')
@login_required
def dashboard():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    courses = [e.course for e in enrollments]

    return render_template('dashboard.html', courses=courses, now=datetime.utcnow)


# ================= ENROLL =================
@app.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):

    existing = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if existing:
        flash("Already enrolled")
        return redirect('/dashboard')

    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()

    flash("Enrolled successfully 🎉")
    return redirect('/dashboard')


# ================= COURSE =================
@app.route('/course/<int:course_id>')
@login_required
def course(course_id):

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        return "You are not enrolled ❌"

    course = Course.query.get_or_404(course_id)
    lectures = Lecture.query.filter_by(course_id=course.id).all()

    return render_template('course.html', course=course, lectures=lectures)


# ================= ADMIN =================
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():

    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':

        form_type = request.form.get('type')

        if form_type == "course":
            course = Course(
                title=request.form['title'],
                description=request.form['description'],
                category=request.form.get('category'),
                price=request.form.get('price', 0)
            )
            db.session.add(course)

        elif form_type == "lecture":
            lecture = Lecture(
                title=request.form['title'],
                video_url=request.form['video_url'],
                course_id=request.form['course_id']
            )
            db.session.add(lecture)

        elif form_type == "blog":
            blog = Blog(
                title=request.form['title'],
                content=request.form['content']
            )
            db.session.add(blog)

        db.session.commit()
        flash("Added successfully ✅")

    return render_template('admin.html')


# ================= LOGOUT =================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)