"""
Auto-Initialize Database on Startup
This runs before the app starts and creates tables if they don't exist
"""

import os
from app import app, db
from models import User, Course

def init_db_if_needed():
    """Initialize database if it doesn't exist"""
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("🔧 First-time setup: Creating admin user and courses...")
            
            # Create admin
            admin = User(
                username='admin',
                email='admin@learnhub.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create 4 featured courses
            courses = [
                Course(
                    title='General Linguistics',
                    description='Comprehensive introduction to linguistic theory and analysis',
                    category='Linguistics',
                    level='Beginner',
                    price=99.00,
                    duration_hours=40,
                    duration_days=60,
                    instructor_name='Dr. Sarah Johnson',
                    featured=True,
                    is_published=True
                ),
                Course(
                    title='Python Programming',
                    description='Complete Python course from basics to advanced',
                    category='Programming',
                    level='Beginner',
                    price=79.00,
                    duration_hours=50,
                    duration_days=90,
                    instructor_name='John Davis',
                    featured=True,
                    is_published=True
                ),
                Course(
                    title='Corpus Linguistics',
                    description='Learn to analyze large text collections using computational methods',
                    category='Linguistics',
                    level='Intermediate',
                    price=129.00,
                    duration_hours=35,
                    duration_days=50,
                    instructor_name='Prof. Michael Chen',
                    featured=True,
                    is_published=True
                ),
                Course(
                    title='Computational Linguistics',
                    description='Advanced course combining linguistics with computer science',
                    category='Linguistics',
                    level='Advanced',
                    price=149.00,
                    duration_hours=45,
                    duration_days=70,
                    instructor_name='Dr. Emily Rodriguez',
                    featured=True,
                    is_published=True
                )
            ]
            
            for course in courses:
                db.session.add(course)
            
            db.session.commit()
            print("✅ Database initialized with admin and 4 courses!")
        else:
            print("✅ Database already exists")

if __name__ == '__main__':
    init_db_if_needed()