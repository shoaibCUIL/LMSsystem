"""
Custom CAPTCHA implementation - Simple Math CAPTCHA
No external dependencies needed!
"""
import random
from flask import session

def generate_math_captcha():
    """
    Generate a simple math CAPTCHA
    Returns: (question, answer)
    """
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    
    operations = [
        ('add', f'{num1} + {num2}', num1 + num2),
        ('subtract', f'{num1 + num2} - {num2}', num1),  # Ensure positive result
        ('multiply', f'{num1} × {num2}', num1 * num2),
    ]
    
    operation = random.choice(operations)
    question = f"What is {operation[1]}?"
    answer = operation[2]
    
    # Store answer in session (server-side)
    session['captcha_answer'] = str(answer)
    
    return question

def verify_math_captcha(user_answer):
    """
    Verify user's CAPTCHA answer
    Returns: True if correct, False otherwise
    """
    if not user_answer:
        return False
    
    correct_answer = session.get('captcha_answer')
    
    if not correct_answer:
        return False
    
    # Clear the answer from session after checking
    session.pop('captcha_answer', None)
    
    # Compare as strings (trim whitespace)
    return str(user_answer).strip() == str(correct_answer).strip()


def generate_question_captcha():
    """
    Generate a question-based CAPTCHA
    Returns: (question, answer)
    """
    questions = [
        ("What is the capital of Pakistan?", "islamabad"),
        ("How many days in a week?", "7"),
        ("What color is the sky?", "blue"),
        ("How many months in a year?", "12"),
        ("What is 2 + 2?", "4"),
        ("The opposite of hot?", "cold"),
        ("The first letter of the alphabet?", "a"),
    ]
    
    question_data = random.choice(questions)
    question = question_data[0]
    answer = question_data[1].lower()
    
    # Store answer in session
    session['captcha_answer'] = answer
    
    return question

def verify_question_captcha(user_answer):
    """
    Verify question-based CAPTCHA
    """
    if not user_answer:
        return False
    
    correct_answer = session.get('captcha_answer', '').lower()
    
    if not correct_answer:
        return False
    
    # Clear the answer
    session.pop('captcha_answer', None)
    
    # Compare (case-insensitive)
    return user_answer.strip().lower() == correct_answer