import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-12345'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///lms.db'
    
    # Fix for Railway PostgreSQL URL
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
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
    RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY') or '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'  # Test key
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY') or '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'  # Test key
    RECAPTCHA_SCORE_THRESHOLD = 0.5
    
    # Email configuration (for future use)
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
    
    # Currency conversion rates (update periodically)
    CURRENCY_RATES = {
        'PKR': 1.0,
        'USD': 0.0036,  # 1 PKR = 0.0036 USD (approx 277 PKR = 1 USD)
        'EUR': 0.0033,  # 1 PKR = 0.0033 EUR
        'GBP': 0.0028,  # 1 PKR = 0.0028 GBP
        'AED': 0.013,   # 1 PKR = 0.013 AED
        'SAR': 0.013,   # 1 PKR = 0.013 SAR
    }
    
    # International pricing multiplier (20% higher for international)
    INTERNATIONAL_MULTIPLIER = 1.2
    
    # Courses configuration
    DEFAULT_COURSES = [
        {
            'title': 'General Linguistics',
            'slug': 'general-linguistics',
            'description': 'Comprehensive introduction to the study of language',
            'level': 'Beginner',
            'duration_estimate': '8 weeks'
        },
        {
            'title': 'Corpus Linguistics',
            'slug': 'corpus-linguistics',
            'description': 'Learn to analyze language using corpus-based methods',
            'level': 'Intermediate',
            'duration_estimate': '10 weeks'
        },
        {
            'title': 'Computational Linguistics',
            'slug': 'computational-linguistics',
            'description': 'Explore the intersection of linguistics and computer science',
            'level': 'Advanced',
            'duration_estimate': '12 weeks'
        }
    ]

def get_config():
    """Factory function to get config"""
    return Config()