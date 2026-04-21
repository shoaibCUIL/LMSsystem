import os
import secrets
import requests
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import current_app, request

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_receipt(file):
    """Save payment receipt and return filename"""
    if file and allowed_file(file.filename, current_app.config['ALLOWED_RECEIPT_EXTENSIONS']):
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{secrets.token_hex(16)}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{extension}"
        
        # Ensure receipts folder exists
        receipts_folder = current_app.config['RECEIPTS_FOLDER']
        os.makedirs(receipts_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(receipts_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

def save_thumbnail(file):
    """Save course thumbnail and return filename"""
    if file and allowed_file(file.filename, current_app.config['ALLOWED_IMAGE_EXTENSIONS']):
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"thumb_{secrets.token_hex(12)}.{extension}"
        
        # Ensure thumbnails folder exists
        thumbnails_folder = current_app.config['THUMBNAILS_FOLDER']
        os.makedirs(thumbnails_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(thumbnails_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

def verify_recaptcha(recaptcha_response):
    """Verify Google reCAPTCHA v3 response"""
    secret_key = current_app.config['RECAPTCHA_SECRET_KEY']
    
    # Skip verification in development with test keys
    if secret_key == '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe':
        return True, 1.0
    
    try:
        payload = {
            'secret': secret_key,
            'response': recaptcha_response,
            'remoteip': request.remote_addr
        }
        
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=payload,
            timeout=10
        )
        
        result = response.json()
        
        if result.get('success'):
            score = result.get('score', 0)
            threshold = current_app.config['RECAPTCHA_SCORE_THRESHOLD']
            return score >= threshold, score
        
        return False, 0
    
    except Exception as e:
        current_app.logger.error(f"reCAPTCHA verification error: {str(e)}")
        return False, 0

def convert_currency(amount_pkr, target_currency='PKR', is_international=False):
    """Convert PKR to target currency"""
    rates = current_app.config['CURRENCY_RATES']
    
    if target_currency not in rates:
        target_currency = 'PKR'
    
    # Apply international multiplier if needed
    if is_international and target_currency != 'PKR':
        amount_pkr *= current_app.config['INTERNATIONAL_MULTIPLIER']
    
    # Convert
    converted_amount = amount_pkr * rates[target_currency]
    
    return round(converted_amount, 2)

def get_currency_from_country(country):
    """Get currency code based on country"""
    currency_map = {
        'Pakistan': 'PKR',
        'United States': 'USD',
        'United Kingdom': 'GBP',
        'UAE': 'AED',
        'Saudi Arabia': 'SAR',
        'Germany': 'EUR',
        'France': 'EUR',
        'Italy': 'EUR',
        'Spain': 'EUR',
    }
    return currency_map.get(country, 'USD')

def calculate_enrollment_dates(days):
    """Calculate enrollment start and expiry dates"""
    now = datetime.utcnow()
    expires_at = now + timedelta(days=days)
    return now, expires_at

def format_currency(amount, currency='PKR'):
    """Format currency with symbol"""
    symbols = {
        'PKR': 'Rs.',
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'AED': 'AED',
        'SAR': 'SAR',
    }
    
    symbol = symbols.get(currency, currency)
    
    if currency == 'PKR':
        return f"{symbol} {amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"

def slugify(text):
    """Create URL-friendly slug from text"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')