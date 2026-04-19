# Add this function RIGHT AFTER your imports and BEFORE any routes
# Place it after login_manager setup

def init_database():
    """Initialize database tables and create admin user if needed"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create admin user if doesn't exist
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
                db.session.commit()
                print('✅ Admin user created: username=admin, password=admin123')
            
            # Check if we have any courses
            course_count = Course.query.count()
            if course_count == 0:
                print('⚠️ No courses found. Run setup_database_FIXED.py to populate courses.')
            else:
                print(f'✅ Database has {course_count} courses')
                
        except Exception as e:
            print(f'❌ Database initialization error: {str(e)}')
            db.session.rollback()


# Call initialization when the module loads (BEFORE any routes are accessed)
init_database()