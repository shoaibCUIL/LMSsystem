"""
Database Migration Script
Add payment tracking, progress tracking, and blog fields
Run this AFTER updating your models.py
"""

from app import app, db
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        print("="*60)
        print("DATABASE MIGRATION - Payment & Progress Tracking")
        print("="*60)
        
        try:
            # Add payment fields to enrollments
            print("\n1. Adding payment tracking fields to enrollments...")
            db.session.execute(text("""
                ALTER TABLE enrollments 
                ADD COLUMN IF NOT EXISTS payment_status VARCHAR(20) DEFAULT 'pending'
            """))
            
            db.session.execute(text("""
                ALTER TABLE enrollments 
                ADD COLUMN IF NOT EXISTS payment_proof_url VARCHAR(500)
            """))
            
            # Add progress fields to enrollments
            print("2. Adding progress tracking fields to enrollments...")
            db.session.execute(text("""
                ALTER TABLE enrollments 
                ADD COLUMN IF NOT EXISTS completed_lectures INTEGER DEFAULT 0
            """))
            
            db.session.execute(text("""
                ALTER TABLE enrollments 
                ADD COLUMN IF NOT EXISTS last_accessed DATETIME
            """))
            
            db.session.execute(text("""
                ALTER TABLE enrollments 
                ADD COLUMN IF NOT EXISTS completed_at DATETIME
            """))
            
            db.session.execute(text("""
                ALTER TABLE enrollments 
                ADD COLUMN IF NOT EXISTS certificate_issued BOOLEAN DEFAULT 0
            """))
            
            # Create lecture_progress table
            print("3. Creating lecture_progress table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS lecture_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    enrollment_id INTEGER NOT NULL,
                    lecture_id INTEGER NOT NULL,
                    completed BOOLEAN DEFAULT 0,
                    completed_at DATETIME,
                    watch_time_seconds INTEGER DEFAULT 0,
                    FOREIGN KEY (enrollment_id) REFERENCES enrollments (id),
                    FOREIGN KEY (lecture_id) REFERENCES lectures (id),
                    UNIQUE (enrollment_id, lecture_id)
                )
            """))
            
            db.session.commit()
            
            print("\n" + "="*60)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("\nNew features added:")
            print("  ✓ Payment tracking (payment_status, payment_proof_url)")
            print("  ✓ Progress tracking (completed_lectures, progress %)")
            print("  ✓ Lecture progress tracking (lecture_progress table)")
            print("  ✓ Course completion tracking")
            print("\n")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            db.session.rollback()
            print("\nMigration failed. Please check the error above.")

if __name__ == '__main__':
    migrate_database()