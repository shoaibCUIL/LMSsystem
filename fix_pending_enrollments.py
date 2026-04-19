"""
DATABASE FIX: Deactivate All Pending Payment Enrollments

Run this ONCE to fix existing enrollments that were incorrectly activated
"""

from app import app, db
from models import Enrollment

def fix_pending_enrollments():
    """Deactivate all enrollments with pending payment status"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("🔧 FIXING PENDING ENROLLMENTS")
        print("="*60 + "\n")
        
        # Find all enrollments with pending payment that are active
        wrong_enrollments = Enrollment.query.filter_by(
            payment_status='pending',
            is_active=True  # ← These should be False!
        ).all()
        
        if not wrong_enrollments:
            print("✅ No enrollments to fix - all good!")
            print("\n" + "="*60)
            return
        
        print(f"Found {len(wrong_enrollments)} enrollments with pending payments that are incorrectly active:")
        print()
        
        for enrollment in wrong_enrollments:
            print(f"  • User: {enrollment.user.username}")
            print(f"    Course: {enrollment.course.title}")
            print(f"    Status: {enrollment.payment_status}")
            print(f"    is_active: {enrollment.is_active} → Setting to FALSE")
            print()
            
            # DEACTIVATE IT
            enrollment.is_active = False
        
        # Commit changes
        db.session.commit()
        
        print("="*60)
        print(f"✅ FIXED {len(wrong_enrollments)} enrollments!")
        print("="*60)
        print("\n📋 Summary:")
        print(f"  • {len(wrong_enrollments)} courses deactivated")
        print("  • Users will need admin approval to access these courses")
        print("  • Courses will appear in dashboard ONLY after payment verification")
        print("\n✨ Done!\n")

if __name__ == '__main__':
    fix_pending_enrollments()