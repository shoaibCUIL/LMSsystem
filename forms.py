from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField, FloatField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from models import User

class RegistrationForm(FlaskForm):
    """Enhanced registration form with all required fields"""
    
    # Basic credentials
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
    
    # Personal information
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=100, message='First name must be 2-100 characters')
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(min=2, max=100, message='Last name must be 2-100 characters')
    ])
    
    # Professional/Academic information
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
    
    # Location
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
    
    # Educational background
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
    
    # reCAPTCHA token (will be submitted via JavaScript)
    recaptcha_token = StringField('Recaptcha Token')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('This email is already registered. Please login or use a different email.')


class LoginForm(FlaskForm):
    """Login form"""
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    remember_me = BooleanField('Remember Me')


class EnrollmentForm(FlaskForm):
    """Course enrollment form"""
    
    # Duration selection
    enrollment_type = SelectField('Enrollment Type', validators=[
        DataRequired(message='Please select enrollment type')
    ], choices=[
        ('', 'Select Duration Type'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('custom_price', 'Custom Price')
    ])
    
    duration_value = IntegerField('Duration', validators=[
        Optional(),
        NumberRange(min=1, message='Duration must be at least 1')
    ])
    
    custom_price = FloatField('Custom Price (PKR)', validators=[
        Optional(),
        NumberRange(min=1500, message='Minimum price is Rs. 1,500')
    ])
    
    # Payment details
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
    
    # Additional notes
    notes = TextAreaField('Additional Notes (Optional)', validators=[
        Optional(),
        Length(max=500)
    ])
    
    def validate_duration_value(self, duration_value):
        """Validate duration based on enrollment type"""
        if self.enrollment_type.data in ['days', 'weeks', 'months']:
            if not duration_value.data:
                raise ValidationError('Please specify the duration')


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
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced')
    ])
    
    duration_estimate = StringField('Duration Estimate', validators=[
        Optional(),
        Length(max=100)
    ])
    
    price_per_day = FloatField('Price per Day (PKR)', validators=[
        DataRequired(),
        NumberRange(min=50, message='Price per day must be at least Rs. 50')
    ])
    
    min_days = IntegerField('Minimum Days', validators=[
        DataRequired(),
        NumberRange(min=1, message='Minimum days must be at least 1')
    ])
    
    min_price_pkr = FloatField('Minimum Price (PKR)', validators=[
        DataRequired(),
        NumberRange(min=100, message='Minimum price must be at least Rs. 100')
    ])
    
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