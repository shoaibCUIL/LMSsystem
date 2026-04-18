"""
Enhanced Course Population Script - FIXED VERSION
Run this to populate your LMS with all 13 courses
"""

from app import app, db
from models import Course
from datetime import datetime

def populate_courses():
    """Add all 13 courses to the database"""
    
    with app.app_context():
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
                'duration_days': 60,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'Corpus Linguistics',
                'description': 'Learn to work with large text collections using corpus linguistic methods. Explore frequency analysis, concordancing, and pattern discovery in real-world language data.',
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
                'description': 'Bridge linguistics and computer science. Learn NLP fundamentals, text processing, language modeling, and how computers understand human language.',
                'category': 'Linguistics',
                'level': 'Advanced',
                'price': 149.00,
                'duration_hours': 45,
                'duration_days': 70,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True
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
                'duration_days': 90,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'Web App Development',
                'description': 'Build modern web applications using Flask, HTML, CSS, JavaScript, and databases. Create responsive, full-stack applications from scratch.',
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
                'description': 'Create professional desktop applications using Python. Learn GUI development with Tkinter, PyQt, and application packaging for distribution.',
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
                'description': 'Automate Google Workspace (Sheets, Docs, Gmail, Drive) with Apps Script. Create custom functions, automated workflows, and productivity tools.',
                'category': 'Programming',
                'level': 'Beginner',
                'price': 89.00,
                'duration_hours': 30,
                'duration_days': 45,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': False
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
                'duration_days': 60,
                'instructor_name': 'AI Specialist',
                'thumbnail_url': '',
                'featured': True
            },
            {
                'title': 'Vibe Coding',
                'description': 'Modern AI-assisted development workflow. Learn to code faster using AI pair programming, prompt engineering for developers, and efficient debugging with AI.',
                'category': 'AI & Automation',
                'level': 'Intermediate',
                'price': 119.00,
                'duration_hours': 25,
                'duration_days': 30,
                'instructor_name': 'AI Specialist',
                'thumbnail_url': '',
                'featured': True
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
                'duration_days': 30,
                'instructor_name': 'Dr. Language Expert',
                'thumbnail_url': '',
                'featured': True
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
                'duration_days': 120,
                'instructor_name': 'Tech Instructor',
                'thumbnail_url': '',
                'featured': True
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
                'duration_days': 50,
                'instructor_name': 'DevOps Expert',
                'thumbnail_url': '',
                'featured': True
            },
        ]
        
        # Add all courses
        added_count = 0
        skipped_count = 0
        
        print("\n" + "="*60)
        print("📚 POPULATING YOUR LMS WITH 13 COURSES")
        print("="*60 + "\n")
        
        for course_data in courses_data:
            # Check if course already exists
            existing = Course.query.filter_by(title=course_data['title']).first()
            if not existing:
                course = Course(**course_data)
                course.created_at = datetime.utcnow()
                db.session.add(course)
                added_count += 1
                print(f"✅ Added: {course_data['title']}")
                print(f"   Category: {course_data['category']} | Price: ${course_data['price']} | Duration: {course_data['duration_days']} days")
            else:
                skipped_count += 1
                print(f"⏭️  Skipped (exists): {course_data['title']}")
        
        db.session.commit()
        
        # Print summary
        print("\n" + "="*60)
        print("✅ COURSE POPULATION COMPLETE!")
        print("="*60)
        print(f"✅ Added: {added_count} new courses")
        print(f"⏭️  Skipped: {skipped_count} existing courses")
        print(f"📊 Total courses in database: {Course.query.count()}")
        
        # Category breakdown
        print("\n📋 Courses by Category:")
        categories = db.session.query(Course.category, db.func.count(Course.id)).group_by(Course.category).all()
        for category, count in categories:
            print(f"   • {category}: {count} courses")
        
        # Price breakdown
        print("\n💰 Price Range:")
        min_price = db.session.query(db.func.min(Course.price)).scalar()
        max_price = db.session.query(db.func.max(Course.price)).scalar()
        avg_price = db.session.query(db.func.avg(Course.price)).scalar()
        print(f"   • Minimum: ${min_price:.2f}")
        print(f"   • Maximum: ${max_price:.2f}")
        print(f"   • Average: ${avg_price:.2f}")
        
        # Duration breakdown
        print("\n⏱️  Duration Range:")
        min_hours = db.session.query(db.func.min(Course.duration_hours)).scalar()
        max_hours = db.session.query(db.func.max(Course.duration_hours)).scalar()
        total_hours = db.session.query(db.func.sum(Course.duration_hours)).scalar()
        print(f"   • Shortest: {min_hours} hours")
        print(f"   • Longest: {max_hours} hours")
        print(f"   • Total content: {total_hours} hours")
        
        print("\n" + "="*60)
        print("🎓 Your LMS is now ready with all courses!")
        print("="*60)
        print("\n📍 Next Steps:")
        print("   1. Visit: http://localhost:5000/courses")
        print("   2. Browse all courses with filters")
        print("   3. Sort by: Price, Duration, Level, Category")
        print("   4. Create custom bundles (15% discount!)")
        print("\n✨ Happy Learning!\n")

if __name__ == '__main__':
    populate_courses()