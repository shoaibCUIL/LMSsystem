"""
Pricing utilities for hourly-based dual currency system
"""
from flask import current_app

def get_currency_for_country(country):
    """Determine currency based on user's country"""
    if country == 'Pakistan':
        return 'pkr'
    else:
        return 'usd'

def get_package_price(level, package_type, currency='pkr'):
    """
    Get price for a package (daily/weekly/monthly)
    
    Args:
        level: 'beginner', 'intermediate', or 'advanced'
        package_type: 'daily', 'weekly', or 'monthly'
        currency: 'pkr' or 'usd'
    
    Returns:
        float: Price for the package
    """
    pricing = current_app.config['PACKAGE_PRICING']
    
    if package_type not in pricing:
        return 0
    
    package = pricing[package_type]
    
    if level not in package:
        return 0
    
    return package[level].get(currency, 0)

def calculate_custom_price(level, hours, currency='pkr'):
    """
    Calculate custom price based on hours
    
    Args:
        level: 'beginner', 'intermediate', or 'advanced'
        hours: Number of hours
        currency: 'pkr' or 'usd'
    
    Returns:
        float: Calculated price
    """
    rates = current_app.config['HOURLY_RATES']
    
    if level not in rates:
        return 0
    
    hourly_rate = rates[level].get(currency, 0)
    return hourly_rate * hours

def apply_multi_course_discount(price, has_multiple_courses=False):
    """
    Apply 10% discount if user has multiple courses
    
    Args:
        price: Original price
        has_multiple_courses: Boolean indicating if user has 2+ courses
    
    Returns:
        tuple: (final_price, discount_amount, has_discount)
    """
    if has_multiple_courses:
        discount_rate = current_app.config.get('MULTI_COURSE_DISCOUNT', 0.10)
        discount = price * discount_rate
        final_price = price - discount
        return final_price, discount, True
    
    return price, 0, False

def format_price(amount, currency='pkr'):
    """
    Format price with currency symbol
    
    Args:
        amount: Price amount
        currency: 'pkr' or 'usd'
    
    Returns:
        str: Formatted price string
    """
    if currency.lower() == 'pkr':
        return f"Rs. {amount:,.0f}"
    else:  # USD
        return f"${amount:,.0f}"

def get_hourly_rate(level, currency='pkr'):
    """
    Get hourly rate for a level
    
    Args:
        level: 'beginner', 'intermediate', or 'advanced'
        currency: 'pkr' or 'usd'
    
    Returns:
        int: Hourly rate
    """
    rates = current_app.config['HOURLY_RATES']
    
    if level not in rates:
        return 0
    
    return rates[level].get(currency, 0)

def get_package_hours(package_type):
    """
    Get number of hours in a package
    
    Args:
        package_type: 'daily', 'weekly', or 'monthly'
    
    Returns:
        int: Number of hours
    """
    pricing = current_app.config['PACKAGE_PRICING']
    
    if package_type not in pricing:
        return 0
    
    return pricing[package_type].get('hours', 0)

def get_level_display_name(level):
    """
    Get display name for level
    
    Args:
        level: 'beginner', 'intermediate', or 'advanced'
    
    Returns:
        str: Capitalized level name
    """
    return level.capitalize() if level else 'Unknown'