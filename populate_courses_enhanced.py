"""
Enhanced Course Population Script - FIXED VERSION
"""

from app import app, db
from models import Course
from datetime import datetime

def populate_courses():
    with app.app_context():
        courses_data = [
            {
                'title': 'General Linguistics',
                'description': 'Master the foundational principles of linguistics, including phonetics, phonology, morphology, syntax, and semantics.',
                'category': 'Linguistics',
                'level': 'Beginner',
                'price': 99.00,
                'duration_hours': 40,
                'duration_days': 60,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'Corpus Linguistics',
                'description': 'Learn to work with large text collections using corpus linguistic methods.',
                'category': 'Linguistics',
                'level': 'Intermediate',
                'price': 129.00,
                'duration_hours': 35,
                'duration_days': 50,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'Computational Linguistics',
                'description': 'Bridge linguistics and computer science. Learn NLP fundamentals, text processing, language modeling.',
                'category': 'Linguistics',
                'level': 'Advanced',
                'price': 149.00,
                'duration_hours': 45,
                'duration_days': 70,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'Python Programming',
                'description': 'Complete Python course from basics to advanced. Learn data structures, OOP, file handling.',
                'category': 'Programming',
                'level': 'Beginner',
                'price': 79.00,
                'duration_hours': 50,
                'duration_days': 90,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'Web App Development',
                'description': 'Build modern web applications using Flask, HTML, CSS, JavaScript, and databases.',
                'category': 'Programming',
                'level': 'Intermediate',
                'price': 149.00,
                'duration_hours': 60,
                'duration_days': 90,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'Desktop App Development',
                'description': 'Create professional desktop applications using Python. Learn GUI development with Tkinter, PyQt.',
                'category': 'Programming',
                'level': 'Intermediate',
                'price': 129.00,
                'duration_hours': 45,
                'duration_days': 60,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': False
            },
            {
                'title': 'Google Apps Script',
                'description': 'Automate Google Workspace with Apps Script. Create custom functions and workflows.',
                'category': 'Programming',
                'level': 'Beginner',
                'price': 89.00,
                'duration_hours': 30,
                'duration_days': 45,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': False
            },
            {
                'title': 'AI Automation',
                'description': 'Harness AI tools and APIs to automate workflows. Integrate ChatGPT, Claude, and other AI services.',
                'category': 'AI & Automation',
                'level': 'Intermediate',
                'price': 159.00,
                'duration_hours': 40,
                'duration_days': 60,
                'instructor_name': 'AI Specialist',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'Vibe Coding',
                'description': 'Modern AI-assisted development workflow. Learn AI pair programming and prompt engineering.',
                'category': 'AI & Automation',
                'level': 'Intermediate',
                'price': 119.00,
                'duration_hours': 25,
                'duration_days': 30,
                'instructor_name': 'AI Specialist',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'Python for Linguists (Short Course)',
                'description': 'Bridge course combining linguistics and programming. Learn Python for text analysis and corpus processing.',
                'category': 'Specialized',
                'level': 'Beginner',
                'price': 69.00,
                'duration_hours': 20,
                'duration_days': 30,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'LMS Development',
                'description': 'Build your own Learning Management System from scratch. Full-stack development with authentication.',
                'category': 'Systems Development',
                'level': 'Advanced',
                'price': 199.00,
                'duration_hours': 70,
                'duration_days': 120,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'How to Deploy and Host Your Tools',
                'description': 'Complete guide to deploying web apps, NLP tools, and APIs. Covers Render, Streamlit, Railway.',
                'category': 'Deployment',
                'level': 'Intermediate',
                'price': 139.00,
                'duration_hours': 35,
                'duration_days': 50,
                'instructor_name': 'DevOps Expert',
                'thumbnail_url': '',
                'featured': True
            },
        ]
        
        added = 0
        skipped = 0
        
        print("\n" + "="*60)
        print("📚 POPULATING YOUR LMS WITH 13 COURSES")
        print("="*60 + "\n")
        
        for data in courses_data:
            existing = Course.query.filter_by(title=data['title']).first()
            if not existing:
                course = Course(**data)
                course.created_at = datetime.utcnow()
                db.session.add(course)
                added += 1
                print(f"✅ {data['title']} - ${data['price']} - {data['duration_days']} days")
            else:
                skipped += 1
                print(f"⏭️  {data['title']} (exists)")
        
        db.session.commit()
        
        print("\n" + "="*60)
        print(f"✅ Added: {added} | Skipped: {skipped} | Total: {Course.query.count()}")
        print("="*60)
        print("\n🎓 Visit: http://localhost:5000/courses\n")

if __name__ == '__main__':
    populate_courses()
