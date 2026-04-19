"""
Initialize Database - Creates all tables and admin user
Run this FIRST before starting the app
"""

from app import app, db
from models import User

def init_database():
    """Create all database tables and admin user"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("🔧 INITIALIZING DATABASE")
        print("="*60 + "\n")
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✅ Tables created successfully!\n")
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@learnhub.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created!\n")
        else:
            print("✅ Admin user already exists\n")
        
        print("="*60)
        print("✅ DATABASE INITIALIZED!")
        print("="*60)
        print("\n📋 Tables created:")
        print("   • users")
        print("   • courses")
        print("   • lectures")
        print("   • enrollments")
        print("   • blogs")
        print("   • bundles")
        print("   • events")
        print("   • tags")
        
        print("\n🔑 Admin Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        
        print("\n📌 Next Steps:")
        print("   1. Run: python populate_courses_enhanced.py")
        print("   2. Start server: python app.py")
        print("   3. Visit: http://localhost:5000\n")

if __name__ == '__main__':
    init_database()