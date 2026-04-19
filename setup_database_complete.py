"""
Complete Database Setup and Diagnostic Script
Fixes all database issues and populates with courses
"""

import os
from datetime import datetime, timedelta
from app import app, db
from models import User, Course

def setup_complete_database():
    """Complete database initialization with courses"""
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔧 COMPLETE DATABASE SETUP")
        print("="*70 + "\n")
        
        # Check if database exists
        db_path = os.path.join(app.root_path, 'instance', 'lms.db')
        if os.path.exists(db_path):
            print(f"📁 Database found at: {db_path}")
            response = input("⚠️  Delete existing database and start fresh? (y/n): ")
            if response.lower() == 'y':
                os.remove(db_path)
                print("🗑️  Old database deleted\n")
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✅ All tables created!\n")
        
        # Create admin user
        print("Creating admin user...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@learnhub.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Admin user created!")
        else:
            print("✅ Admin user already exists")
        
        # Create your 12 courses
        print("\nCreating courses...")
        
        courses_data = [
            {
                'title': 'General Linguistics',
                'description': 'Comprehensive introduction to linguistic theory and analysis. Master the fundamentals of language structure, phonetics, syntax, and semantics.',
                'category': 'Linguistics',
                'level': 'Beginner',
                'price': 99.00,
                'duration_hours': 40,
                'duration_days': 60,
                'instructor_name': 'Dr. Sarah Johnson',
                'is_free': False,
                'featured': True,
                'is_published': True
            },
            {
                'title': 'Corpus Linguistics',
                'description': 'Learn to analyze large text collections using computational methods. Explore corpus design, annotation, and statistical analysis.',
                'category': 'Linguistics',
                'level': 'Intermediate',
                'price': 129.00,
                'duration_hours': 35,
                'duration_days': 50,
                'instructor_name': 'Prof. Michael Chen',
                'is_free': False,
                'featured': True,
                'is_published': True
            },
            {
                'title': 'Computational Linguistics',
                'description': 'Advanced course combining linguistics with computer science. Learn NLP, language modeling, and AI applications.',
                'category': 'Linguistics',
                'level': 'Advanced',
                'price': 149.00,
                'duration_hours': 45,
                'duration_days': 70,
                'instructor_name': 'Dr. Emily Rodriguez',
                'is_free': False,
                'featured': True,
                'is_published': True
            },
            {
                'title': 'Python Programming',
                'description': 'Complete Python course from basics to advanced. Build real projects and master modern Python development.',
                'category': 'Programming',
                'level': 'Beginner',
                'price': 79.00,
                'duration_hours': 50,
                'duration_days': 90,
                'instructor_name': 'John Davis',
                'is_free': False,
                'featured': True,
                'is_published': True
            },
            {
                'title': 'Web App Development',
                'description': '🔜 COMING SOON - Build modern web applications with Flask, React, and databases.',
                'category': 'Programming',
                'level': 'Intermediate',
                'price': 149.00,
                'duration_hours': 60,
                'duration_days': 90,
                'instructor_name': 'Alex Martinez',
                'is_free': False,
                'featured': False,
                'is_published': True
            },
            {
                'title': 'Desktop App Development',
                'description': 'Create professional desktop applications using modern frameworks and best practices.',
                'category': 'Programming',
                'level': 'Intermediate',
                'price': 129.00,
                'duration_hours': 45,
                'duration_days': 60,
                'instructor_name': 'David Wilson',
                'is_free': False,
                'featured': False,
                'is_published': True
            },
            {
                'title': 'Google Apps Script',
                'description': '🔜 COMING SOON - Automate Google Workspace with Apps Script. Build custom solutions.',
                'category': 'Automation',
                'level': 'Beginner',
                'price': 89.00,
                'duration_hours': 30,
                'duration_days': 45,
                'instructor_name': 'Lisa Anderson',
                'is_free': False,
                'featured': False,
                'is_published': True
            },
            {
                'title': 'AI Automation',
                'description': '🔜 COMING SOON - Leverage AI to automate workflows and boost productivity.',
                'category': 'AI',
                'level': 'Advanced',
                'price': 159.00,
                'duration_hours': 40,
                'duration_days': 60,
                'instructor_name': 'Dr. James Taylor',
                'is_free': False,
                'featured': False,
                'is_published': True
            },
            {
                'title': 'Vibe Coding',
                'description': '🔜 COMING SOON - Creative coding and generative art. Express yourself through code.',
                'category': 'Programming',
                'level': 'Intermediate',
                'price': 119.00,
                'duration_hours': 25,
                'duration_days': 30,
                'instructor_name': 'Sophie Lee',
                'is_free': False,
                'featured': False,
                'is_published': True
            },
            {
                'title': 'Python for Linguists',
                'description': 'Specialized Python course for linguistic research and text analysis.',
                'category': 'Linguistics',
                'level': 'Beginner',
                'price': 69.00,
                'duration_hours': 20,
                'duration_days': 30,
                'instructor_name': 'Dr. Rachel Green',
                'is_free': False,
                'featured': False,
                'is_published': True
            },
            {
                'title': 'LMS Development',
                'description': '🔜 COMING SOON - Build your own Learning Management System from scratch.',
                'category': 'Programming',
                'level': 'Advanced',
                'price': 199.00,
                'duration_hours': 70,
                'duration_days': 120,
                'instructor_name': 'Mark Thompson',
                'is_free': False,
                'featured': False,
                'is_published': True
            },
            {
                'title': 'How to Deploy and Host Your Tools',
                'description': '🔜 COMING SOON - Learn deployment strategies, hosting options, and DevOps basics.',
                'category': 'DevOps',
                'level': 'Intermediate',
                'price': 139.00,
                'duration_hours': 35,
                'duration_days': 50,
                'instructor_name': 'Chris Brown',
                'is_free': False,
                'featured': False,
                'is_published': True
            }
        ]
        
        courses_created = 0
        for course_data in courses_data:
            existing = Course.query.filter_by(title=course_data['title']).first()
            if not existing:
                course = Course(**course_data)
                db.session.add(course)
                courses_created += 1
        
        db.session.commit()
        
        if courses_created > 0:
            print(f"✅ Created {courses_created} courses!")
        else:
            print(f"✅ All 12 courses already exist")
        
        # Final summary
        total_courses = Course.query.count()
        total_users = User.query.count()
        
        print("\n" + "="*70)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"   • Total Users: {total_users}")
        print(f"   • Total Courses: {total_courses}")
        print(f"   • Featured Courses: {Course.query.filter_by(featured=True).count()}")
        print(f"   • Coming Soon: 6 courses")
        
        print("\n🔑 Login Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        
        print("\n🚀 Next Steps:")
        print("   1. Start server: python app.py")
        print("   2. Visit: http://localhost:5000")
        print("   3. Login and explore!")
        print()

if __name__ == '__main__':
    setup_complete_database()