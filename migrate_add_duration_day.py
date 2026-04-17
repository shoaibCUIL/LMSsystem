"""
Database Migration: Add duration_days field to Course model
Run this BEFORE populating courses if you have an existing database
"""

from app import app, db
from sqlalchemy import text

def add_duration_days_field():
    """Add duration_days column to courses table"""
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(courses)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'duration_days' in columns:
                print("✅ duration_days field already exists!")
                return
            
            # Add the column
            print("Adding duration_days field to courses table...")
            db.session.execute(text("ALTER TABLE courses ADD COLUMN duration_days INTEGER DEFAULT 30"))
            db.session.commit()
            
            print("✅ Successfully added duration_days field!")
            print("   Default value: 30 days")
            print("\nYou can now run populate_courses.py")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_duration_days_field()