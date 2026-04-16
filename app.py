from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'  # later Railway DB

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# ------------------ MODELS ------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    return "LMS Running 🚀"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(email=request.form['email'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return "Welcome to Dashboard 🎓"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# ------------------ RUN ------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)