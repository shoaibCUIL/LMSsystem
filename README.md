# LMS Platform - Linguistics Learning Management System

A comprehensive Learning Management System for teaching General Linguistics, Corpus Linguistics, and Computational Linguistics courses with enrollment management, payment verification, and strong security features.

## 🎯 Features

### User Management
- ✅ User registration with extended profile (name, designation, city, country, education, university)
- ✅ Secure login/logout with session management
- ✅ Google reCAPTCHA v3 integration for bot protection
- ✅ Role-based access control (User/Admin)

### Course Enrollment System
- ✅ Flexible pricing: By days, weeks, months, or custom price
- ✅ Minimum 2 days enrollment, minimum Rs. 1,500
- ✅ International pricing (20% higher for non-Pakistan users)
- ✅ Automatic price calculation based on duration
- ✅ Automatic duration calculation based on price

### Payment System
- ✅ Multiple payment methods:
  - JazzCash: +92-3414763186
  - Easypaisa: +92-3414763186
  - Bank Transfer: Meezan Bank (Account: 04110104042981, IBAN: PK41MEZN0004110104042981)
- ✅ Payment receipt upload (JPG, PNG, PDF)
- ✅ Admin approval workflow
- ✅ Enrollment status tracking (pending/approved/rejected/expired)

### Course Management
- ✅ Course creation and management
- ✅ Lecture management with video support
- ✅ Free preview lectures
- ✅ Access control based on enrollment status
- ✅ Course thumbnails

### Admin Features
- ✅ Dashboard with statistics
- ✅ Enrollment approval/rejection
- ✅ Course and lecture management
- ✅ User management
- ✅ Payment receipt verification

## 📋 Requirements

- Python 3.11+
- PostgreSQL (for production) or SQLite (for development)
- Railway account (for deployment)
- Google reCAPTCHA v3 keys

## 🚀 Local Development Setup

### Step 1: Clone and Setup

```bash
# Navigate to your project directory
cd LMSSystem

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# Important: Change SECRET_KEY in production!
```

### Step 3: Database Initialization

```bash
# Initialize database with default data
flask init-db

# This creates:
# - Admin user: admin@lms.com / admin123
# - Three default courses (General Linguistics, Corpus Linguistics, Computational Linguistics)
```

### Step 4: Create Additional Admin (Optional)

```bash
flask create-admin
# Follow prompts to create a custom admin user
```

### Step 5: Run Development Server

```bash
# Run the application
python app.py

# Or using Flask CLI:
flask run
```

Visit: http://localhost:5000

## 🌐 Railway Deployment

### Step 1: Prepare for Deployment

1. Make sure all files are committed to Git:
```bash
git add .
git commit -m "Initial LMS commit"
```

2. Push to GitHub:
```bash
git remote add origin https://github.com/yourusername/lms-system.git
git push -u origin main
```

### Step 2: Railway Setup

1. Go to [Railway.app](https://railway.app/)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your LMS repository
5. Railway will automatically detect it's a Flask app

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "New" → "Database" → "PostgreSQL"
2. Railway automatically sets `DATABASE_URL` environment variable
3. Your app will use this automatically

### Step 4: Set Environment Variables

In Railway project settings → Variables, add:

```
SECRET_KEY=your-super-secret-random-key-here-change-this
FLASK_ENV=production
RECAPTCHA_SITE_KEY=your-recaptcha-site-key
RECAPTCHA_SECRET_KEY=your-recaptcha-secret-key
```

### Step 5: Initialize Production Database

1. Open Railway project's deployment
2. Click on "Deployments" → Latest deployment → "View Logs"
3. Once deployed, go to the web service and run:

```bash
# Railway provides a shell - use it to run:
flask init-db
```

Alternatively, create admin via code by adding this route temporarily:
```python
@app.route('/create-first-admin')
def create_first_admin():
    # Add admin creation logic
    # Remove this route after first admin is created!
```

### Step 6: Configure Domain (Optional)

1. In Railway project → Settings → Domains
2. Railway provides a free `.railway.app` domain
3. You can also add a custom domain

## 🔐 Getting reCAPTCHA Keys

1. Go to [Google reCAPTCHA Admin](https://www.google.com/recaptcha/admin)
2. Register a new site
3. Choose reCAPTCHA v3
4. Add your domain (for local: `localhost`, for production: your Railway domain)
5. Copy Site Key and Secret Key to `.env`

## 📁 Project Structure

```
LMSSystem/
├── app.py                 # Main application factory
├── config.py             # Configuration settings
├── models.py             # Database models
├── forms.py              # WTForms form definitions
├── routes.py             # Main routes (auth, courses, dashboard)
├── admin_routes.py       # Admin routes (enrollment approval, course management)
├── utils.py              # Utility functions (CAPTCHA, file upload, currency)
├── requirements.txt      # Python dependencies
├── Procfile             # Railway deployment config
├── runtime.txt          # Python version specification
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore patterns
├── templates/           # HTML templates
│   ├── base.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── courses/
│   │   ├── enroll.html
│   │   ├── course_detail.html
│   │   └── lecture.html
│   ├── dashboard/
│   │   ├── dashboard.html
│   │   ├── enrollments.html
│   │   └── profile.html
│   ├── admin/
│   │   ├── admin.html
│   │   ├── enrollments.html
│   │   ├── enrollment_detail.html
│   │   └── courses.html
│   └── public/
│       ├── home.html
│       └── courses.html
├── uploads/             # File uploads
│   ├── receipts/       # Payment receipts
│   └── thumbnails/     # Course thumbnails
└── logs/               # Application logs
```

## 🎓 Default Courses

The system comes with three pre-configured courses:

1. **General Linguistics**
   - Level: Beginner
   - Duration: 8 weeks
   - Comprehensive introduction to language study

2. **Corpus Linguistics**
   - Level: Intermediate
   - Duration: 10 weeks
   - Corpus-based language analysis methods

3. **Computational Linguistics**
   - Level: Advanced
   - Duration: 12 weeks
   - Linguistics meets computer science

## 💰 Pricing Structure

- **Base Rate**: Rs. 75 per day
- **Minimum Duration**: 2 days
- **Minimum Price**: Rs. 1,500
- **International Multiplier**: 1.2x (20% higher for non-Pakistan users)

### Examples:
- 2 days: Rs. 1,500 (minimum)
- 1 week (7 days): Rs. 525
- 1 month (30 days): Rs. 2,250
- Custom Rs. 3,000: ~40 days access

## 🔑 Default Admin Credentials

**After running `flask init-db`:**
- Email: `admin@lms.com`
- Password: `admin123`

**⚠️ IMPORTANT**: Change this immediately in production!

## 🛠️ Common Tasks

### Create New Admin User
```bash
flask create-admin
```

### Database Migrations (After Model Changes)
```bash
flask db init                    # First time only
flask db migrate -m "description"
flask db upgrade
```

### View Logs
```bash
tail -f logs/lms.log
```

## 📧 Contact Information

For payment issues or support:
- **Email**: shoaibtahir411@gmail.com
- **JazzCash/Easypaisa**: +92-3414763186
- **Bank**: Meezan Bank (Muhammad Shoaib Tahir)

## 🐛 Troubleshooting

### Issue: reCAPTCHA not working locally
**Solution**: Use the test keys provided in config.py, or register localhost in your reCAPTCHA settings

### Issue: Database connection error on Railway
**Solution**: 
1. Ensure PostgreSQL add-on is installed
2. Check `DATABASE_URL` is set in environment variables
3. Restart the deployment

### Issue: File uploads not working
**Solution**:
1. Check `uploads/receipts` and `uploads/thumbnails` directories exist
2. Verify file size is under 16MB
3. Check file extension is allowed

### Issue: Can't approve enrollments
**Solution**:
1. Make sure you're logged in as admin
2. Check `is_admin=True` in database for your user
3. Run: `UPDATE users SET is_admin=true WHERE email='your@email.com';`

## 🔒 Security Features

- ✅ Password hashing with Werkzeug
- ✅ CSRF protection on all forms
- ✅ reCAPTCHA v3 bot protection
- ✅ Secure session management
- ✅ File upload validation
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (Jinja2 auto-escaping)

## 📝 License

© 2025 Muhammad Shoaib Tahir. All rights reserved.

## 🤝 Support

For technical support or questions:
1. Check this README first
2. Review the troubleshooting section
3. Email: shoaibtahir411@gmail.com