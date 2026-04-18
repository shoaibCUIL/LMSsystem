"""
Reset Database with New Schema
This will delete the old database and create a fresh one with all the new fields
"""

from app import app, db
from models import User, Course, Lecture, Enrollment, Blog, CustomBundle, LectureProgress
import os

def reset_database():
    """Reset database with new schema"""
    
    with app.app_context():
        # Get database path
        db_path = os.path.join(app.root_path, 'instance', 'lms.db')
        
        print("\n" + "="*60)
        print("🔄 DATABASE RESET STARTED")
        print("="*60 + "\n")
        
        # Delete old database if exists
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Old database deleted")
        
        # Create all tables
        db.create_all()
        print("✅ New database created with updated schema")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@learnhub.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_admin=False
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        
        db.session.commit()
        
        print("✅ Admin user created (username: admin, password: admin123)")
        print("✅ Test user created (username: testuser, password: test123)")
        
        print("\n" + "="*60)
        print("✅ DATABASE RESET COMPLETE!")
        print("="*60)
        print("\n📋 Tables created:")
        print("   • users")
        print("   • courses")
        print("   • lectures")
        print("   • enrollments (WITH payment & progress tracking)")
        print("   • lecture_progress (NEW!)")
        print("   • blogs")
        print("   • bundles")
        print("   • events")
        print("   • tags")
        
        print("\n🔑 Login Credentials:")
        print("   Admin: username=admin, password=admin123")
        print("   Test User: username=testuser, password=test123")
        
        print("\n📍 Next Steps:")
        print("   1. Run: python populate_courses_enhanced.py")
        print("   2. Start server: python app.py")
        print("   3. Visit: http://localhost:5000")
        print("\n✨ Done!\n")

if __name__ == '__main__':
    reset_database()