from flask import Flask, render_template, request, redirect, flash, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from config import Config
from models import db, User, Course, Lecture, Enrollment

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ================= LOAD USER =================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ================= INIT DB =================
with app.app_context():
    db.create_all()


# ================= HOME =================
@app.route('/')
def home():
    courses = Course.query.all()
    return render_template('public/home.html', courses=courses)


# ================= COURSES =================
@app.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template('public/courses.html', courses=courses)


# ================= BLOGS =================
@app.route('/blogs')
def blogs():
    return render_template('public/blogs.html', blogs=[])


# ================= EVENTS =================
@app.route('/events')
def events():
    return render_template('public/events.html', events=[])


# ================= DISCUSSIONS =================
@app.route('/discussions')
def discussions():
    return "<h2>Discussion forum coming soon 💬</h2>"


# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        if request.form['password'] != request.form['confirm_password']:
            flash("Passwords do not match ❌")
            return redirect('/register')

        hashed_password = generate_password_hash(request.form['password'])

        user = User(
            email=request.form['email'],
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully ✅")
        return redirect('/login')

    return render_template('register.html')


# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect('/dashboard')
        else:
            flash("Invalid email or password ❌")

    return render_template('login.html')


# ================= DASHBOARD =================
@app.route('/dashboard')
@login_required
def dashboard():

    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    courses = [e.course for e in enrollments]

    return render_template(
        'dashboard.html',
        courses=courses,
        now=datetime.utcnow
    )


# ================= ENROLL =================
@app.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):

    existing = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if existing:
        flash("Already enrolled ✅")
        return redirect('/dashboard')

    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()

    flash("Enrolled successfully 🎉")
    return redirect('/dashboard')


# ================= COURSE PAGE =================
@app.route('/course/<int:course_id>')
@login_required
def course(course_id):

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        return "You are not enrolled in this course ❌"

    if enrollment.expiry_date < datetime.utcnow():
        return "Your course access expired ⛔"

    course = Course.query.get_or_404(course_id)
    lectures = Lecture.query.filter_by(course_id=course.id).all()

    return render_template('course.html', course=course, lectures=lectures)


# ================= ADMIN PANEL =================
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():

    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':

        form_type = request.form.get('type')

        # -------- COURSE --------
        if form_type == "course":
            course = Course(
                title=request.form['title'],
                description=request.form['description']
            )
            db.session.add(course)

        # -------- LECTURE --------
        elif form_type == "lecture":
            lecture = Lecture(
                title=request.form['title'],
                video_url=request.form['video_url'],
                course_id=request.form['course_id']
            )
            db.session.add(lecture)

        # -------- BLOG --------
        elif form_type == "blog":
            flash("Blog feature coming soon ✍️")

        # -------- EVENT --------
        elif form_type == "event":
            flash("Event feature coming soon 📅")

        db.session.commit()
        flash("Action completed successfully ✅")

    return render_template('admin.html')


# ================= LOGOUT =================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)