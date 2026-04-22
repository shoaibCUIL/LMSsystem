import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from database import db

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Initialize extensions
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'info'
    
    # Setup logging
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
    
    # Ensure upload directories exist
    os.makedirs(app.config['RECEIPTS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['THUMBNAILS_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes import auth_bp, course_bp, dashboard_bp, main_bp
    from admin_routes import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Context processors
    @app.context_processor
    def inject_config():
        """Make config available in templates"""
        return {'config': app.config}
    
    # Shell context for flask shell
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
    
    # CLI commands
    @app.cli.command()
    def init_db():
        """Initialize the database with default data"""
        from models import User, Course
        from utils import slugify
        
        db.create_all()
        
        # Create default admin user if not exists
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
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print('✓ Admin user created: admin@lms.com / admin123')
        
        # Create courses with custom pricing
        courses_config = [
            {
                'title': 'General Linguistics',
                'slug': 'general-linguistics',
                'description': 'Comprehensive introduction to the study of language',
                'level': 'Beginner',
                'duration_estimate': '1 month',
                'price_per_month': 5500.0,  # Monthly price
                'min_days': 30,  # 1 month minimum
                'min_price_pkr': 5500.0
            },
            {
                'title': 'Corpus Linguistics',
                'slug': 'corpus-linguistics',
                'description': 'Learn to analyze language using corpus-based methods',
                'level': 'Intermediate',
                'duration_estimate': '1 month',
                'price_per_month': 8500.0,  # Monthly price
                'min_days': 30,  # 1 month minimum
                'min_price_pkr': 8500.0
            },
            {
                'title': 'Computational Linguistics',
                'slug': 'computational-linguistics',
                'description': 'Explore the intersection of linguistics and computer science',
                'level': 'Advanced',
                'duration_estimate': '1 month',
                'price_per_month': 12500.0,  # Monthly price
                'min_days': 30,  # 1 month minimum
                'min_price_pkr': 12500.0
            }
        ]
        
        for course_data in courses_config:
            existing = Course.query.filter_by(slug=course_data['slug']).first()
            if not existing:
                # Calculate price per day from monthly price
                price_per_day = course_data['price_per_month'] / 30.0
                
                course = Course(
                    title=course_data['title'],
                    slug=course_data['slug'],
                    description=course_data['description'],
                    level=course_data['level'],
                    duration_estimate=course_data['duration_estimate'],
                    price_per_day=price_per_day,
                    min_days=course_data['min_days'],
                    min_price_pkr=course_data['min_price_pkr'],
                    is_active=True
                )
                db.session.add(course)
                print(f'✓ Course created: {course.title} - Rs. {course_data["price_per_month"]}/month')
        
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
            is_admin=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f'✓ Admin user created: {email}')
    
    return app


# For development
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)