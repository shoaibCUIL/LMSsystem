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
    UPLOAD_FOLDER    = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    RECEIPTS_FOLDER  = os.path.join(UPLOAD_FOLDER, 'receipts')
    THUMBNAILS_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbnails')

    MAX_CONTENT_LENGTH       = 16 * 1024 * 1024
    ALLOWED_RECEIPT_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    ALLOWED_IMAGE_EXTENSIONS   = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE      = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY    = True
    SESSION_COOKIE_SAMESITE    = 'Lax'

    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE   = os.environ.get('FLASK_ENV') == 'production'
    REMEMBER_COOKIE_HTTPONLY = True

    # reCAPTCHA v3
    RECAPTCHA_SITE_KEY        = os.environ.get('RECAPTCHA_SITE_KEY')   or '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    RECAPTCHA_SECRET_KEY      = os.environ.get('RECAPTCHA_SECRET_KEY') or '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
    RECAPTCHA_SCORE_THRESHOLD = 0.5

    # Email
    MAIL_SERVER         = os.environ.get('MAIL_SERVER')
    MAIL_PORT           = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS        = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@lms.com'

    # Payment info
    PAYMENT_INFO = {
        'jazzcash':  {'number': '+92-3414763186', 'account_name': 'Muhammad Shoaib Tahir'},
        'easypaisa': {'number': '+92-3414763186', 'account_name': 'Muhammad Shoaib Tahir'},
        'bank': {
            'bank_name':      'Meezan Bank',
            'account_title':  'Muhammad Shoaib Tahir',
            'account_number': '04110104042981',
            'iban':           'PK41MEZN0004110104042981',
        },
        'contact_email': 'shoaibtahir411@gmail.com',
    }

    # Currency
    CURRENCY_RATES = {
        'PKR': 1.0,   'USD': 0.0036, 'GBP': 0.0028,
        'EUR': 0.0033, 'AED': 0.013,  'SAR': 0.013,
    }
    INTERNATIONAL_MULTIPLIER = 2.0

    # ─────────────────────────────────────────────────────────
    # DURATION-TIER PRICING  (Option A — student picks tier)
    # Tier price depends on course level: beginner/intermediate/advanced
    # ─────────────────────────────────────────────────────────
    DURATION_TIERS = {
        'short': {
            'label':        'Short — 1 Month',
            'months':       1,
            'total_days':   30,
            'beginner':     {'pkr': 4000,  'usd': 30},
            'intermediate': {'pkr': 6000,  'usd': 45},
            'advanced':     {'pkr': 8000,  'usd': 60},
        },
        'standard': {
            'label':        'Standard — 2 Months',
            'months':       2,
            'total_days':   60,
            'beginner':     {'pkr': 8000,  'usd': 60},
            'intermediate': {'pkr': 11000, 'usd': 85},
            'advanced':     {'pkr': 15000, 'usd': 120},
        },
        'intensive': {
            'label':        'Intensive — 3 Months',
            'months':       3,
            'total_days':   90,
            'beginner':     {'pkr': 15000, 'usd': 120},
            'intermediate': {'pkr': 22000, 'usd': 170},
            'advanced':     {'pkr': 35000, 'usd': 250},
        },
    }

    # ─────────────────────────────────────────────────────────
    # PACKAGE / BUNDLE PLANS
    # ─────────────────────────────────────────────────────────
    PACKAGE_PLANS = {
        'starter': {
            'label':       '🟢 Starter — 1 Month',
            'months':      1,
            'total_days':  30,
            'courses':     1,
            'pkr':         3000,
            'usd':         20,
            'description': '1 course of your choice for 1 month.',
        },
        'pro': {
            'label':       '🔵 Pro — 2 Months',
            'months':      2,
            'total_days':  60,
            'courses':     3,
            'pkr_min':     10000,
            'pkr_max':     15000,
            'usd_min':     80,
            'usd_max':     120,
            'description': '2–3 courses for 2 months.',
        },
        'elite': {
            'label':       '🔴 Elite — 3 Months (Full Access)',
            'months':      3,
            'total_days':  90,
            'courses':     'all',
            'pkr_min':     20000,
            'pkr_max':     30000,
            'usd_min':     150,
            'usd_max':     220,
            'description': 'All courses, full access for 3 months.',
        },
    }

    # Legacy stubs — kept so existing code doesn't break
    HOURLY_RATES = {
        'beginner':     {'pkr': 800,  'usd': 6},
        'intermediate': {'pkr': 1200, 'usd': 10},
        'advanced':     {'pkr': 2000, 'usd': 16},
    }
    PACKAGE_PRICING       = {}   # replaced by DURATION_TIERS
    ADD_ON_PRICING        = {
        'guided_support':            {'pkr': 5000,  'usd': 40},
        'one_on_one_mentorship_min': {'pkr': 12000, 'usd': 100},
        'one_on_one_mentorship_max': {'pkr': 20000, 'usd': 160},
        'custom_plan_min':           {'pkr': 2000,  'usd': 20},
        'custom_plan_max':           {'pkr': 5000,  'usd': 40},
    }
    MULTI_COURSE_DISCOUNT = 0.10

    # ─────────────────────────────────────────────────────────
    # DEFAULT COURSES  (7 courses)
    # ─────────────────────────────────────────────────────────
    DEFAULT_COURSES = [
        {
            'title':             'General Linguistics',
            'slug':              'general-linguistics',
            'description':       'Comprehensive introduction to phonetics, morphology, syntax, semantics, and the science of human language.',
            'level':             'beginner',
            'duration_estimate': '4–6 weeks',
            'hourly_rate_pkr':   800,
            'hourly_rate_usd':   6,
        },
        {
            'title':             'Python for Linguists',
            'slug':              'python-for-linguists',
            'description':       'Learn Python programming tailored for language analysis, text processing, and linguistic research workflows.',
            'level':             'beginner',
            'duration_estimate': '6–8 weeks',
            'hourly_rate_pkr':   800,
            'hourly_rate_usd':   6,
        },
        {
            'title':             'Corpus Linguistics',
            'slug':              'corpus-linguistics',
            'description':       'Analyse large language datasets, identify patterns, and draw evidence-based conclusions from real text corpora.',
            'level':             'intermediate',
            'duration_estimate': '8–10 weeks',
            'hourly_rate_pkr':   1200,
            'hourly_rate_usd':   10,
        },
        {
            'title':             'Python Full Course',
            'slug':              'python-full-course',
            'description':       'Intensive end-to-end Python course covering data structures, OOP, file handling, APIs, and NLP libraries.',
            'level':             'intermediate',
            'duration_estimate': '10–12 weeks',
            'hourly_rate_pkr':   1200,
            'hourly_rate_usd':   10,
        },
        {
            'title':             'Coding with AI',
            'slug':              'coding-with-ai',
            'description':       'Practical course on using AI tools and LLMs to accelerate coding, automate tasks, and build AI-assisted projects.',
            'level':             'intermediate',
            'duration_estimate': '8–10 weeks',
            'hourly_rate_pkr':   1200,
            'hourly_rate_usd':   10,
        },
        {
            'title':             'Computational Linguistics',
            'slug':              'computational-linguistics',
            'description':       'Three-level programme — Basics → Techniques → Projects. Covers NLP fundamentals, language modelling, and AI language systems.',
            'level':             'advanced',
            'duration_estimate': '12 weeks (3 levels)',
            'hourly_rate_pkr':   2000,
            'hourly_rate_usd':   16,
        },
        {
            'title':             'Statistics for Corpus Linguistics',
            'slug':              'stats-for-corpus',
            'description':       'Applied statistics for corpus researchers: frequency analysis, collocations, chi-square, log-likelihood, and R/Python tools.',
            'level':             'advanced',
            'duration_estimate': '10–12 weeks',
            'hourly_rate_pkr':   2000,
            'hourly_rate_usd':   16,
        },
    ]


def get_config():
    """Factory function to get config"""
    return Config()