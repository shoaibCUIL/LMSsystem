from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField, FloatField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from models import User

class RegistrationForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address'),
        Length(max=120)
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=100, message='First name must be 2-100 characters')
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(min=2, max=100, message='Last name must be 2-100 characters')
    ])
    
    designation = SelectField('Designation', validators=[
        DataRequired(message='Please select your designation')
    ], choices=[
        ('', 'Select Designation'),
        ('Student', 'Student'),
        ('Undergraduate Student', 'Undergraduate Student'),
        ('Graduate Student', 'Graduate Student'),
        ('PhD Scholar', 'PhD Scholar'),
        ('Research Scholar', 'Research Scholar'),
        ('Faculty Member', 'Faculty Member'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Professor', 'Professor'),
        ('Researcher', 'Researcher'),
        ('Professional', 'Professional'),
        ('Linguist', 'Linguist'),
        ('Language Teacher', 'Language Teacher'),
        ('Other', 'Other')
    ])
    
    city = StringField('City', validators=[
        DataRequired(message='City is required'),
        Length(min=2, max=100)
    ])
    
    country = SelectField('Country', validators=[
        DataRequired(message='Please select your country')
    ], choices=[
        ('', 'Select Country'),
        ('Pakistan', 'Pakistan'),
        ('India', 'India'),
        ('Bangladesh', 'Bangladesh'),
        ('United States', 'United States'),
        ('United Kingdom', 'United Kingdom'),
        ('Canada', 'Canada'),
        ('Australia', 'Australia'),
        ('UAE', 'United Arab Emirates'),
        ('Saudi Arabia', 'Saudi Arabia'),
        ('Germany', 'Germany'),
        ('France', 'France'),
        ('China', 'China'),
        ('Japan', 'Japan'),
        ('Other', 'Other')
    ])
    
    education = SelectField('Highest Education', validators=[
        DataRequired(message='Please select your education level')
    ], choices=[
        ('', 'Select Education Level'),
        ('High School', 'High School / Secondary'),
        ('Intermediate', 'Intermediate / A-Levels'),
        ('Bachelor', "Bachelor's Degree"),
        ('Master', "Master's Degree"),
        ('MPhil', 'MPhil'),
        ('PhD', 'PhD / Doctorate'),
        ('Other', 'Other')
    ])
    
    university = StringField('University / Institution', validators=[
        DataRequired(message='University/Institution name is required'),
        Length(min=2, max=200)
    ])
    
    captcha_answer = StringField('Security Question', validators=[
        DataRequired(message='Please answer the security question')
    ])
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('This email is already registered. Please login or use a different email.')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    remember_me = BooleanField('Remember Me')


class EnrollmentForm(FlaskForm):
    enrollment_type = SelectField('Select Package', validators=[
        DataRequired(message='Please select a package')
    ], choices=[
        ('', 'Select Package'),
        ('daily', 'Daily (5 hours)'),
        ('weekly', 'Weekly (25 hours)'),
        ('monthly', 'Monthly (100 hours)'),
        ('custom_hours', 'Custom Hours')
    ])
    
    custom_hours = IntegerField('Number of Hours', validators=[
        Optional(),
        NumberRange(min=1, message='Minimum 1 hour')
    ])
    
    payment_method = SelectField('Payment Method', validators=[
        DataRequired(message='Please select payment method')
    ], choices=[
        ('', 'Select Payment Method'),
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'Easypaisa'),
        ('bank', 'Bank Transfer (Meezan Bank)')
    ])
    
    payment_receipt = FileField('Payment Receipt', validators=[
        FileRequired(message='Please upload payment receipt'),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Only JPG, PNG, and PDF files are allowed')
    ])
    
    notes = TextAreaField('Additional Notes (Optional)', validators=[
        Optional(),
        Length(max=500)
    ])


class CourseForm(FlaskForm):
    """Admin form for creating/editing courses"""
    title = StringField('Course Title', validators=[
        DataRequired(),
        Length(min=5, max=200)
    ])
    
    description = TextAreaField('Short Description', validators=[
        DataRequired(),
        Length(min=20, max=500)
    ])
    
    detailed_description = TextAreaField('Detailed Description')
    
    level = SelectField('Level', choices=[
        ('beginner', 'Beginner'),      # ✅ lowercase to match model default
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    
    duration_estimate = StringField('Duration Estimate', validators=[
        Optional(),
        Length(max=100)
    ])
    
    # ✅ Fixed: matches model fields hourly_rate_pkr and hourly_rate_usd
    hourly_rate_pkr = IntegerField('Hourly Rate (PKR)', validators=[
        DataRequired(),
        NumberRange(min=100, message='Minimum rate is Rs. 100/hour')
    ], default=800)
    
    hourly_rate_usd = IntegerField('Hourly Rate (USD)', validators=[
        DataRequired(),
        NumberRange(min=1, message='Minimum rate is $1/hour')
    ], default=6)
    
    thumbnail = FileField('Course Thumbnail', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    
    is_active = BooleanField('Active')


class LectureForm(FlaskForm):
    """Admin form for creating/editing lectures"""
    title = StringField('Lecture Title', validators=[
        DataRequired(),
        Length(min=5, max=200)
    ])
    
    description = TextAreaField('Description')
    content = TextAreaField('Content (HTML supported)')
    video_url = StringField('Video URL', validators=[Optional()])
    order_number = IntegerField('Order Number', default=0)
    is_free = BooleanField('Free Preview')
    duration_minutes = IntegerField('Duration (minutes)', validators=[Optional()])