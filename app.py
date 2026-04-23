import os
import logging
from datetime import datetime
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from database import db

from dotenv import load_dotenv
load_dotenv()

login_manager = LoginManager()
migrate = Migrate()


def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'info'
    
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/lms.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('LMS startup')
    
    os.makedirs(app.config['RECEIPTS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['THUMBNAILS_FOLDER'], exist_ok=True)
    
    from routes import auth_bp, course_bp, dashboard_bp, main_bp
    from admin_routes import admin_bp
    from discussion_routes import discussion_bp
    app.register_blueprint(discussion_bp)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    @app.context_processor
    def inject_globals():
        """Make common variables available in all templates"""
        return {
            'config': app.config,
            'app_name': 'EduLearn',
            'now': datetime.utcnow(),  # FIX: used in base.html footer as {{ now.year }}
        }
    
    @app.shell_context_processor
    def make_shell_context():
        from models import User, Course, Enrollment, Lecture, Blog, Event, CustomBundle, Tag
        return {
            'db': db,
            'User': User,
            'Course': Course,
            'Enrollment': Enrollment,
            'Lecture': Lecture,
            'Blog': Blog,
            'Event': Event,
            'CustomBundle': CustomBundle,
            'Tag': Tag
        }
    
    @app.cli.command()
    def init_db():
        """Initialize the database with default data"""
        from models import User, Course
        from utils import slugify
        
        db.create_all()
        
        admin = User.query.filter_by(email='admin@lms.com').first()
        if not admin:
            admin = User(
                email='admin@lms.com',
                first_name='Admin',
                last_name='User',
                designation='Administrator',
                city='Karachi',
                country='Pakistan',
                education='Master',
                university='LMS University',
                is_admin=True,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print('✓ Admin user created: admin@lms.com / admin123')
        else:
            if not admin.is_active:
                admin.is_active = True
                print('✓ Existing admin account activated')
            if not admin.is_admin:
                admin.is_admin = True
                print('✓ Existing admin privileges restored')
        
        for course_data in app.config['DEFAULT_COURSES']:
            existing = Course.query.filter_by(slug=course_data['slug']).first()
            if not existing:
                course = Course(
                    title=course_data['title'],
                    slug=course_data['slug'],
                    description=course_data['description'],
                    level=course_data['level'],
                    duration_estimate=course_data['duration_estimate'],
                    hourly_rate_pkr=course_data['hourly_rate_pkr'],
                    hourly_rate_usd=course_data['hourly_rate_usd'],
                    is_active=True
                )
                db.session.add(course)
                print(f'✓ Course created: {course.title}')
        
        db.session.commit()
        print('\n✓ Database initialized successfully!')
    
    @app.cli.command()
    def create_admin():
        """Create a new admin user"""
        import click
        from models import User
        
        email = click.prompt('Email')
        password = click.prompt('Password', hide_input=True, confirmation_prompt=True)
        first_name = click.prompt('First Name')
        last_name = click.prompt('Last Name')
        
        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f'User with email {email} already exists!')
            return
        
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            designation='Administrator',
            city='Admin City',
            country='Pakistan',
            education='Master',
            university='Admin University',
            is_admin=True,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f'✓ Admin user created: {email}')

    @app.cli.command()
    def fix_admin():
        """Fix existing admin account if inactive or missing admin flag"""
        from models import User
        
        admin = User.query.filter_by(email='admin@lms.com').first()
        if not admin:
            print('No admin@lms.com account found. Run flask init_db first.')
            return
        
        changed = False
        if not admin.is_active:
            admin.is_active = True
            changed = True
            print('✓ Admin account activated')
        if not admin.is_admin:
            admin.is_admin = True
            changed = True
            print('✓ Admin flag set')
        
        if changed:
            db.session.commit()
            print('✓ Admin account fixed successfully')
        else:
            print('Admin account is already active and has admin privileges')
    
    return app


# At the bottom of app.py, add this outside __main__
# Add this line so gunicorn can find it
app = create_app()

with app.app_context():
    from database import db
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)