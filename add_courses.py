from app import create_app
from database import db
from models import Course

app = create_app()
with app.app_context():
    courses = [
        {
            'title': 'Corpus Linguistics',
            'slug': 'corpus-linguistics',
            'description': 'Explore the study of language through large collections of real-world text and speech data.',
            'detailed_description': 'This course covers corpus design, annotation, frequency analysis, concordancing, and the use of corpus tools for linguistic research.',
            'level': 'intermediate',
            'hourly_rate_pkr': 200,
            'hourly_rate_usd': 8,
            'duration_estimate': '3 months',
            'is_active': True
        },
        {
            'title': 'General Linguistics',
            'slug': 'general-linguistics',
            'description': 'A comprehensive introduction to the scientific study of language structure and use.',
            'detailed_description': 'Covers phonetics, phonology, morphology, syntax, semantics, and pragmatics with real-world examples.',
            'level': 'beginner',
            'hourly_rate_pkr': 200,
            'hourly_rate_usd': 8,
            'duration_estimate': '2 months',
            'is_active': True
        },
        {
            'title': 'Computational Linguistics',
            'slug': 'computational-linguistics',
            'description': 'Learn how computers process and understand human language using NLP techniques.',
            'detailed_description': 'Topics include tokenization, POS tagging, parsing, sentiment analysis, machine translation, and language models.',
            'level': 'advanced',
            'hourly_rate_pkr': 200,
            'hourly_rate_usd': 8,
            'duration_estimate': '4 months',
            'is_active': True
        },
        {
            'title': 'LMS Development',
            'slug': 'lms-development',
            'description': 'Build a full-featured Learning Management System using Python and Flask.',
            'detailed_description': 'Learn to develop LMS platforms with user authentication, course management, payment integration, and admin dashboards.',
            'level': 'intermediate',
            'hourly_rate_pkr': 200,
            'hourly_rate_usd': 8,
            'duration_estimate': '3 months',
            'is_active': True
        },
        {
            'title': 'Coding with AI',
            'slug': 'coding-with-ai',
            'description': 'Master modern AI-assisted coding tools and techniques to supercharge your development workflow.',
            'detailed_description': 'Covers GitHub Copilot, ChatGPT for coding, prompt engineering for developers, AI debugging, and building AI-powered apps.',
            'level': 'beginner',
            'hourly_rate_pkr': 200,
            'hourly_rate_usd': 8,
            'duration_estimate': '2 months',
            'is_active': True
        },
    ]

    for c in courses:
        existing = Course.query.filter_by(slug=c['slug']).first()
        if not existing:
            course = Course(**c)
            db.session.add(course)
            print('Added: ' + c['title'])
        else:
            print('Already exists: ' + c['title'])

    db.session.commit()
    print('Done!')