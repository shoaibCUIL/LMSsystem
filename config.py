import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-12345'
    
    # Database - safely handle postgres:// -> postgresql:// for Railway
    _db_url = os.environ.get('DATABASE_URL') or 'sqlite:///lms.db'
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # File uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    RECEIPTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'receipts')
    THUMBNAILS_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbnails')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_RECEIPT_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    REMEMBER_COOKIE_HTTPONLY = True
    
    # reCAPTCHA v3 (Google)
    RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY') or '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY') or '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
    RECAPTCHA_SCORE_THRESHOLD = 0.5
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@lms.com'
    
    # Payment information
    PAYMENT_INFO = {
        'jazzcash': {
            'number': '+92-3414763186',
            'account_name': 'Muhammad Shoaib Tahir'
        },
        'easypaisa': {
            'number': '+92-3414763186',
            'account_name': 'Muhammad Shoaib Tahir'
        },
        'bank': {
            'bank_name': 'Meezan Bank',
            'account_title': 'Muhammad Shoaib Tahir',
            'account_number': '04110104042981',
            'iban': 'PK41MEZN0004110104042981'
        },
        'contact_email': 'shoaibtahir411@gmail.com'
    }

    CURRENCY_RATES = {
        'PKR': 1.0,
        'USD': 0.0036,
        'GBP': 0.0028,
        'EUR': 0.0033,
        'AED': 0.013,
        'SAR': 0.013,
    }

    INTERNATIONAL_MULTIPLIER = 2.0

    # Hourly-Based Pricing Structure (Dual Currency)
    HOURLY_RATES = {
        'beginner': {
            'pkr': 800,
            'usd': 6
        },
        'intermediate': {
            'pkr': 1200,
            'usd': 10
        },
        'advanced': {
            'pkr': 2000,
            'usd': 16
        }
    }
    
    # Package Pricing
    PACKAGE_PRICING = {
        'daily': {
            'hours': 5,
            'discount': 0.10,
            'beginner':     {'pkr': 3600,   'usd': 27},
            'intermediate': {'pkr': 5400,   'usd': 45},
            'advanced':     {'pkr': 9000,   'usd': 72}
        },
        'weekly': {
            'hours': 25,
            'discount': 0.20,
            'beginner':     {'pkr': 16000,  'usd': 120},
            'intermediate': {'pkr': 24000,  'usd': 200},
            'advanced':     {'pkr': 40000,  'usd': 320}
        },
        'monthly': {
            'hours': 100,
            'discount': 0.30,
            'beginner':     {'pkr': 56000,  'usd': 420},
            'intermediate': {'pkr': 84000,  'usd': 700},
            'advanced':     {'pkr': 140000, 'usd': 1120}
        }
    }
    
    # Add-on Services
    ADD_ON_PRICING = {
        'guided_support':               {'pkr': 5000,  'usd': 40},
        'one_on_one_mentorship_min':     {'pkr': 12000, 'usd': 100},
        'one_on_one_mentorship_max':     {'pkr': 20000, 'usd': 160},
        'custom_plan_min':               {'pkr': 2000,  'usd': 20},
        'custom_plan_max':               {'pkr': 5000,  'usd': 40}
    }
    
    # Multi-course discount
    MULTI_COURSE_DISCOUNT = 0.10
    
    # Default courses
    DEFAULT_COURSES = [
        {
            'title': 'General Linguistics',
            'slug': 'general-linguistics',
            'description': 'Comprehensive introduction to the study of language. Perfect for beginners starting their linguistics journey.',
            'level': 'beginner',
            'duration_estimate': '8 weeks',
            'hourly_rate_pkr': 800,
            'hourly_rate_usd': 6
        },
        {
            'title': 'Corpus Linguistics',
            'slug': 'corpus-linguistics',
            'description': 'Learn to analyze language using corpus-based methods and computational tools. Intermediate level course.',
            'level': 'intermediate',
            'duration_estimate': '10 weeks',
            'hourly_rate_pkr': 1200,
            'hourly_rate_usd': 10
        },
        {
            'title': 'Computational Linguistics',
            'slug': 'computational-linguistics',
            'description': 'Explore the intersection of linguistics and computer science. Advanced course requiring programming knowledge.',
            'level': 'advanced',
            'duration_estimate': '12 weeks',
            'hourly_rate_pkr': 2000,
            'hourly_rate_usd': 16
        }
    ]


def get_config():
    """Factory function to get config"""
    return Config()