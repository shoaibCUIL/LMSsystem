from flask import Flask, render_template, request, redirect, url_for, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime

from config import Config
from models import db, User, Course, Lecture

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ------------------ LOAD USER ------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ------------------ HOME ------------------

@app.route('/')
def home():
    return "LMS Running 🚀"


# ------------------ REGISTER ------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            email=request.form['email'],
            password=request.form['password']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


# ------------------ LOGIN ------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user and user.password == request.form['password']:
            login_user(user)
            return redirect('/dashboard')

    return render_template('login.html')


# ------------------ DASHBOARD ------------------

@app.route('/dashboard')
@login_required
def dashboard():
    courses = Course.query.all()
    return render_template('dashboard.html', courses=courses)


# ------------------ COURSE PAGE ------------------

@app.route('/course/<int:course_id>')
@login_required
def course(course_id):
    course = Course.query.get_or_404(course_id)

    # 🔐 Expiry check
    if current_user.expiry_date < datetime.utcnow():
        return "Your access has expired ⛔"

    lectures = Lecture.query.filter_by(course_id=course.id).all()

    return render_template('course.html', course=course, lectures=lectures)


# ------------------ ADMIN PANEL ------------------

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():

    # Only admin allowed
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':

        # Add Course
        if request.form['type'] == "course":
            course = Course(
                title=request.form['title'],
                description=request.form['description']
            )
            db.session.add(course)
            db.session.commit()

        # Add Lecture
        elif request.form['type'] == "lecture":
            lecture = Lecture(
                title=request.form['title'],
                video_url=request.form['video_url'],
                course_id=request.form['course_id']
            )
            db.session.add(lecture)
            db.session.commit()

    return render_template('admin.html')


# ------------------ LOGOUT ------------------

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


# ------------------ CREATE DB ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)