"""
Course Population Script - Your LMS Courses
Run this after first starting the app to populate with your courses
"""

from app import app, db
from models import Course
from datetime import datetime

def populate_courses():
    """Add all courses to the database"""
    
    with app.app_context():
        # Clear existing courses (optional - remove if you want to keep existing)
        # Course.query.delete()
        
        courses_data = [
            # ==========================================
            # A. LINGUISTICS (Theoretical + Applied)
            # ==========================================
            {
                'title': 'General Linguistics',
                'description': 'Master the foundational principles of linguistics, including phonetics, phonology, morphology, syntax, and semantics. Perfect for beginners and those seeking a comprehensive understanding of language structure.',
                'category': 'Linguistics',
                'level': 'Beginner',
                'price': 99.00,
                'duration_hours': 40,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True,
                'is_free': False
            },
            {
                'title': 'Corpus Linguistics',
                'description': 'Learn to work with large text collections using corpus linguistic methods. Explore frequency analysis, concordancing, and pattern discovery in real-world language data.',
                'category': 'Linguistics',
                'level': 'Intermediate',
                'price': 129.00,
                'duration_hours': 35,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True,
                'is_free': False
            },
            {
                'title': 'Computational Linguistics',
                'description': 'Bridge linguistics and computer science. Learn NLP fundamentals, text processing, language modeling, and how computers understand human language.',
                'category': 'Linguistics',
                'level': 'Advanced',
                'price': 149.00,
                'duration_hours': 45,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True,
                'is_free': False
            },
            
            # ==========================================
            # B. PROGRAMMING & DEVELOPMENT
            # ==========================================
            {
                'title': 'Python Programming',
                'description': 'Complete Python course from basics to advanced. Learn data structures, OOP, file handling, error handling, and real-world application development.',
                'category': 'Programming',
                'level': 'Beginner',
                'price': 79.00,
                'duration_hours': 50,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': True,
                'is_free': False
            },
            {
                'title': 'Web App Development',
                'description': 'Build modern web applications using Flask, HTML, CSS, JavaScript, and databases. Create responsive, full-stack applications from scratch.',
                'category': 'Programming',
                'level': 'Intermediate',
                'price': 149.00,
                'duration_hours': 60,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': True,
                'is_free': False
            },
            {
                'title': 'Desktop App Development',
                'description': 'Create professional desktop applications using Python. Learn GUI development with Tkinter, PyQt, and application packaging for distribution.',
                'category': 'Programming',
                'level': 'Intermediate',
                'price': 129.00,
                'duration_hours': 45,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': False,
                'is_free': False
            },
            {
                'title': 'Google Apps Script',
                'description': 'Automate Google Workspace (Sheets, Docs, Gmail, Drive) with Apps Script. Create custom functions, automated workflows, and productivity tools.',
                'category': 'Programming',
                'level': 'Beginner',
                'price': 89.00,
                'duration_hours': 30,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': False,
                'is_free': False
            },
            
            # ==========================================
            # C. AI & AUTOMATION
            # ==========================================
            {
                'title': 'AI Automation',
                'description': 'Harness AI tools and APIs to automate workflows. Learn to integrate ChatGPT, Claude, and other AI services into your applications and processes.',
                'category': 'AI & Automation',
                'level': 'Intermediate',
                'price': 159.00,
                'duration_hours': 40,
                'instructor_name': 'AI Specialist',
                'thumbnail_url': '',
                'featured': True,
                'is_free': False
            },
            {
                'title': 'Vibe Coding',
                'description': 'Modern AI-assisted development workflow. Learn to code faster using AI pair programming, prompt engineering for developers, and efficient debugging with AI.',
                'category': 'AI & Automation',
                'level': 'Intermediate',
                'price': 119.00,
                'duration_hours': 25,
                'instructor_name': 'AI Specialist',
                'thumbnail_url': '',
                'featured': True,
                'is_free': False
            },
            
            # ==========================================
            # D. SPECIALIZED / NICHE COURSES
            # ==========================================
            {
                'title': 'Python for Linguists (Short Course)',
                'description': 'Bridge course combining linguistics and programming. Learn Python specifically for text analysis, corpus processing, and linguistic research. Perfect for linguists entering computational work.',
                'category': 'Specialized',
                'level': 'Beginner',
                'price': 69.00,
                'duration_hours': 20,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True,
                'is_free': False
            },
            
            # ==========================================
            # E. SYSTEMS & TOOLS DEVELOPMENT
            # ==========================================
            {
                'title': 'LMS Development',
                'description': 'Build your own Learning Management System from scratch. Learn full-stack development, database design, user authentication, course management, and payment integration.',
                'category': 'Systems Development',
                'level': 'Advanced',
                'price': 199.00,
                'duration_hours': 70,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': True,
                'is_free': False
            },
            
            # ==========================================
            # F. DEPLOYMENT & HOSTING
            # ==========================================
            {
                'title': 'How to Deploy and Host Your Tools',
                'description': 'Complete guide to deploying and hosting web apps, NLP tools, and APIs. Master deployment fundamentals, server management, domains, and scaling. Covers Render, Streamlit, Railway, and more.',
                'category': 'Deployment',
                'level': 'Intermediate',
                'price': 139.00,
                'duration_hours': 35,
                'instructor_name': 'DevOps Expert',
                'thumbnail_url': '',
                'featured': True,
                'is_free': False
            },
        ]
        
        # Add all courses
        added_count = 0
        for course_data in courses_data:
            # Check if course already exists
            existing = Course.query.filter_by(title=course_data['title']).first()
            if not existing:
                course = Course(**course_data)
                course.created_at = datetime.utcnow()
                db.session.add(course)
                added_count += 1
                print(f"✅ Added: {course_data['title']}")
            else:
                print(f"⏭️  Skipped (exists): {course_data['title']}")
        
        db.session.commit()
        
        print(f"\n{'='*50}")
        print(f"✅ Course Population Complete!")
        print(f"{'='*50}")
        print(f"Added: {added_count} new courses")
        print(f"Total courses in database: {Course.query.count()}")
        print(f"\nCourses by category:")
        
        categories = db.session.query(Course.category, db.func.count(Course.id)).group_by(Course.category).all()
        for category, count in categories:
            print(f"  • {category}: {count} courses")

if __name__ == '__main__':
    print("Starting course population...")
    populate_courses()
    print("\n✅ Done! Visit http://localhost:5000/courses to see your courses!")